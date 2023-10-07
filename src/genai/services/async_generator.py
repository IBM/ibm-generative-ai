import asyncio
import heapq
import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from signal import SIGINT, SIGTERM, signal
from typing import Optional

from genai.exceptions import GenAiException
from genai.options import Options
from genai.schemas.responses import GenerateResponse, TokenizeResponse
from genai.services.connection_manager import ConnectionManager
from genai.services.service_interface import ServiceInterface
from genai.utils.errors import to_genai_error

logger = logging.getLogger(__name__)

__all__ = ["AsyncResponseGenerator"]


class AsyncResponseGenerator:
    def __init__(
        self,
        model_id,
        prompts,
        params,
        service: ServiceInterface,
        fn="generate",
        ordered=False,
        callback=None,
        options: Optional[Options] = None,
        *,
        throw_on_error: bool = False,
        max_concurrency_limit: Optional[int] = None,
    ):
        """Instantiates the ConcurrentWrapper Interface.

        Args:
            model_id (str): The type of model to use
            prompts (list): List of prompts
            params (GenerateParams): Parameters to use during generate requests
            service (ServiceInterface): The service interface
            fn (Literal["generate", "tokenize"]): Function to call from service
            callback (Callable[[GenerateResult], Any]): callback to execute once a prompt is successfully received.
        """
        self.model_id = model_id
        self.prompts = prompts
        self.params = params
        self.service = service
        self.callback = callback
        self.fn = fn
        self.ordered = ordered
        self.options = options
        self.throw_on_error = throw_on_error
        self._client_close_fn = None
        self._is_terminating = False
        self._max_concurrency_limit = max_concurrency_limit

    def __enter__(self):
        self._accumulator = []
        self._initialize_fn_specific_params()
        self._queue = Queue()
        self._loop = asyncio.new_event_loop()
        self._is_terminating = False
        return self

    def _shutdown(self):
        pending = asyncio.all_tasks(self._loop)
        for t in pending:
            t.cancel()
        if self._loop.is_running():
            self._loop.stop()
        while not self._queue.empty():
            _ = self._queue.get()
            self._queue.task_done()
        self._queue.join()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._shutdown()
        except Exception as e:
            logger.error(str(e))
            raise to_genai_error(e)

    def _initialize_fn_specific_params(self):
        if self.fn == "generate":
            self._batch_size = 1
            self._num_batches = len(self.prompts)
            self._message_type = GenerateResponse
            self._service_fn = self.service.async_generate
            ConnectionManager.make_generate_client()
            self._client_close_fn = ConnectionManager.delete_generate_client
        elif self.fn == "tokenize":
            self._batch_size = 5
            a, b = divmod(len(self.prompts), self._batch_size)
            self._num_batches = a + (b > 0)
            self._message_type = TokenizeResponse
            self._service_fn = self.service.async_tokenize
            ConnectionManager.make_tokenize_client()
            self._client_close_fn = ConnectionManager.delete_tokenize_client

    def _generate_batch(self):
        for i in range(0, len(self.prompts), self._batch_size):
            yield self.prompts[i : min(i + self._batch_size, len(self.prompts))]

    def _process_response(self, response, batch_size):
        if response is None:
            for _ in range(batch_size):
                yield None
        else:
            for result in response.results:
                yield result

    async def _get_response_json(self, model, inputs, params, options):
        try:
            response_raw = await self._service_fn(model, inputs, params, options)
            response = response_raw.json()
            if response_raw and (200 < response_raw.status_code or response_raw.status_code > 299):
                raise Exception(response)
        except Exception as ex:
            logger.error("Error in _get_response_json {}: {}".format(type(ex), str(ex)))
            if self.throw_on_error:
                raise ex
            response = None
        return response

    async def _task(self, inputs, batch_num):
        if self._is_terminating:
            self._queue.put_nowait(
                (
                    batch_num,
                    len(inputs),
                    None,
                    GenAiException("Generation has been aborted by the user."),
                )
            )
            return

        response = None
        try:
            response = await self._get_response_json(self.model_id, inputs, self.params, self.options)
            logger.debug("Received response = {}".format(response))
            for i in range(len(response["results"])):
                response["results"][i]["input_text"] = inputs[i]
            response = self._message_type(**response)
            logger.debug("Cast to Response = {}".format(response))
        except Exception as e:
            logger.error(
                "Exception raised async_generate and casting : {}, response = {}, inputs = {}".format(
                    str(e), response, inputs
                )
            )
            self._queue.put_nowait((batch_num, len(inputs), None, to_genai_error(e)))
            return
        try:
            self._queue.put_nowait((batch_num, len(inputs), response, None))
            if self.callback is not None:
                for result in response.results:
                    self.callback(result)
        except Exception as e:
            logger.error(
                "Exception raised in callback : {}, response = {}, inputs = {}".format(str(e), response, inputs)
            )

    async def _schedule_requests(self):
        async def get_limits():
            if self.fn == "tokenize":
                return len(self.prompts)

            limits = self.service.generate_limits()
            tokens_remaining = limits.tokenCapacity - limits.tokensUsed
            if self._max_concurrency_limit is not None and self._max_concurrency_limit > 0:
                return min(self._max_concurrency_limit, tokens_remaining)
            return tokens_remaining

        tasks = []
        remaining_tokens = await get_limits()
        for idx, batch in enumerate(self._generate_batch()):
            while remaining_tokens <= 0:
                await asyncio.sleep(1)
                remaining_tokens = await get_limits()

            remaining_tokens -= 1
            logger.debug("Creating task for batch_num {}".format(idx))
            task = asyncio.create_task(self._task(batch, idx))
            tasks.append(task)

        await asyncio.gather(*tasks)

    def _request_launcher(self):
        try:
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._schedule_requests())
        except Exception as ex:
            self.throw_on_error = True
            self._queue.put_nowait((1, 1, None, ex))
            raise ex
        finally:
            self._loop.run_until_complete(self._cleanup())

    async def _cleanup(self):
        if self._client_close_fn is not None:
            await self._client_close_fn()

    def generate_response(
        self,
    ):  # -> Generator[Union[GenerateResult, TokenizeResult, None]]:
        """Method to spawn a launcher thread to launch requests for generate endpoint
        and yield responses as they get received.

        Yields:
            Generator[Union[GenerateResult, TokenizeResult, None]]: A generator of results
        """
        if len(self.prompts) == 0:
            return

        with ThreadPoolExecutor(max_workers=1) as executor:

            def init_termination(*args):
                self._is_terminating = True
                executor.shutdown(cancel_futures=False, wait=False)

            signal(SIGTERM, init_termination)
            signal(SIGINT, init_termination)

            task = executor.submit(self._request_launcher)

            counter = 0
            minheap, batch_tracker = [], 0
            while counter < self._num_batches:
                try:
                    batch_num, batch_size, response, error = self._queue.get()
                    self._queue.task_done()
                    if task.exception() is not None:
                        raise task.exception()
                except Exception as ex:
                    logger.error("Exception while reading from queue: {}".format(str(ex)))
                    raise ex
                else:
                    counter += 1
                    # FUTURE: Add metadata here as follows if necessary:
                    # if response is not None:
                    #   for i in len(response.results):
                    #     response.results[i].metadata = self.metadata[batch_num * BATCH_SIZE + i]
                    if not self.ordered:
                        if self.throw_on_error and error:
                            raise error

                        for result in self._process_response(response, batch_size):
                            yield result
                        continue
                try:
                    # If we are here then self.ordered is True.
                    heapq.heappush(minheap, (batch_num, batch_size, response, error))
                    for i in range(len(minheap)):
                        bnum, bsize, resp, error = heapq.heappop(minheap)
                        if bnum == batch_tracker:
                            if self.throw_on_error and error:
                                raise error
                            for result in self._process_response(resp, bsize):
                                yield result
                            batch_tracker += 1
                        else:
                            heapq.heappush(minheap, (bnum, bsize, resp, error))
                            break
                except Exception as ex:
                    logger.error("Error in heap processing: {}".format(str(ex)))
                    raise ex
