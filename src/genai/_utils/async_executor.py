import asyncio
import logging
from asyncio import AbstractEventLoop, Task
from collections.abc import Iterator
from concurrent.futures import CancelledError, Future
from contextlib import suppress
from typing import Awaitable, Callable, Generator, Generic, Optional, TypeVar, Union

from genai._utils.general import first_defined, single_execution
from genai._utils.http_client.httpx_client import AsyncHttpxClient
from genai._utils.limiters.base_limiter import BaseLimiter
from genai._utils.limiters.container_limiter import LimiterContainer
from genai._utils.limiters.shared_limiter import LoopBoundLimiter
from genai._utils.queues.flushable_queue import FlushableQueue
from genai._utils.queues.ordered_queue import OrderedQueue

__all__ = ["execute_async", "BaseConfig"]

from genai._utils.shared_loop import shared_event_loop

TInput = TypeVar("TInput")
TResult = TypeVar("TResult")


logger = logging.getLogger(__name__)


class BaseConfig:
    __slots__ = ()
    ordered: bool = False
    throw_on_error: bool = True
    limit_reach_retry_threshold: float = 1.0
    concurrency_limit: Optional[int] = None


class _AsyncGenerator(Generic[TInput, TResult]):
    """
    Utility iterator to process 'inputs' asynchronously by spawning new thread with it's own event loop.
    Communication is done via Queues.
    """

    def __init__(
        self,
        *,
        inputs: list[TInput],
        http_client: Callable[[], AsyncHttpxClient],
        handler: Callable[[TInput, AsyncHttpxClient, BaseLimiter], Awaitable[TResult]],
        limiters: Optional[list[Optional[LoopBoundLimiter]]] = None,
        ordered: Optional[bool] = None,
        throw_on_error: Optional[bool] = None,
    ):
        self._inputs = inputs
        self._http_client_factory = http_client
        self._handler = handler
        self._limiters = limiters
        self._ordered = first_defined(ordered, default=BaseConfig.ordered)
        self._throw_on_error = first_defined(throw_on_error, default=BaseConfig.throw_on_error)

        self._queue: Union[OrderedQueue, FlushableQueue] = OrderedQueue() if ordered else FlushableQueue()
        self._irrecoverable_error = False
        self._future: Optional[Future] = None

    def _add_to_queue(
        self,
        *,
        idx: Optional[int],
        result: Optional[TResult],
        error: Optional[Exception],
    ):
        entry = idx, result, error
        self._queue.put_nowait(entry)

    async def _process_input(
        self,
        limiter: BaseLimiter,
        batch_num: int,
        input: TInput,
        client: AsyncHttpxClient,
    ):
        async with limiter:
            logger.debug(f"Creating task for batch_num: {batch_num}")
            try:
                response = await self._handler(input, client, limiter)
                logger.debug("Received response = {}".format(response))
                self._add_to_queue(idx=batch_num, result=response, error=None)
            except Exception as e:
                logger.error(f"Exception raised during processing\n{str(e)}")
                self._add_to_queue(idx=batch_num, result=None, error=e)

    async def _schedule_requests(self, limiter: BaseLimiter, loop: AbstractEventLoop):
        tasks: list[Task] = []
        try:
            async with self._http_client_factory() as client:
                tasks.extend(
                    loop.create_task(self._process_input(limiter, idx, input, client))
                    for idx, input in enumerate(self._inputs)
                )
                await asyncio.gather(*tasks)
        except Exception as ex:
            self._irrecoverable_error = True
            self._add_to_queue(idx=None, result=None, error=ex)
            raise ex
        finally:
            for task in tasks:
                task.cancel()

    @single_execution
    def _handle_close_signal(self):
        if not self._future:
            return
        self._future.cancel()
        self._queue.flush()
        self._irrecoverable_error = True
        self._add_to_queue(
            idx=None,
            result=None,
            error=InterruptedError("Generation has been aborted by the user."),
        )

    def create_iterator(self) -> Iterator[TResult]:
        if not self._inputs:
            return
        with shared_event_loop as loop:
            limiter = LimiterContainer(*(self._limiters or []))
            self._future = asyncio.run_coroutine_threadsafe(self._schedule_requests(limiter, loop), loop)

            shared_event_loop.add_close_handler(self._handle_close_signal)
            try:
                for _ in enumerate(self._inputs):
                    batch_num, response, error = self._queue.get()
                    self._queue.task_done()

                    if (self._throw_on_error or self._irrecoverable_error) and error:
                        raise error

                    yield response
            except Exception:
                # future is PENDING even if there are running tasks due to implementation of run_coroutine_threadsafe
                # therefore cancel always succeeds
                self._future.cancel()
                raise
            finally:
                with suppress(CancelledError):
                    self._future.result()
                self._queue.flush()
                shared_event_loop.remove_close_handler(self._handle_close_signal)

    def __iter__(self) -> Iterator[TResult]:
        return self.create_iterator()


def execute_async(
    *,
    inputs: list[TInput],
    http_client: Callable[[], AsyncHttpxClient],
    handler: Callable[[TInput, AsyncHttpxClient, BaseLimiter], Awaitable[TResult]],
    limiters: Optional[list[Optional[LoopBoundLimiter]]] = None,
    ordered: Optional[bool] = None,
    throw_on_error: Optional[bool] = None,
) -> Generator[TResult, None, None]:
    yield from _AsyncGenerator(
        inputs=inputs,
        http_client=http_client,
        handler=handler,
        limiters=limiters,
        ordered=ordered,
        throw_on_error=throw_on_error,
    )
