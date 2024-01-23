import asyncio
import logging
from typing import Awaitable, Callable

from pydantic import BaseModel, Field

from genai._utils.asyncio_future import AsyncioLock
from genai._utils.limiters.adjustable_semaphor import AdjustableAsyncSemaphore
from genai._utils.limiters.base_limiter import BaseLimiter

__all__ = ["ExternalLimiter", "ExternalLimiterHandler", "ConcurrencyResponse"]


class ConcurrencyResponse(BaseModel):
    limit: int = Field(..., ge=1, description="Maximum number of concurrent requests")
    remaining: int = Field(..., ge=0, description="Number of remaining requests before reaching the limit")


ExternalLimiterHandler = Callable[[], Awaitable[ConcurrencyResponse]]


class ExternalLimiter(BaseLimiter):
    """A limiter class that interacts with an external handler to enforce dynamic concurrent limits."""

    limit_block_recheck_internal_ms: int = 100

    def __init__(self, *, handler: ExternalLimiterHandler):
        self._handler = handler
        self._lock = AsyncioLock()
        self._sp = AdjustableAsyncSemaphore(0)
        self._max_limit = 0
        self._synced = False
        self._logger = logging.getLogger(self.__module__)

    def _change_limit(self, new_limit: int):
        old_limit = self._sp.limit

        limit_has_changed = self._sp.change_max_limit(new_limit)
        if limit_has_changed:
            self._logger.debug(f"Changing limit from {old_limit} to {new_limit}")

    async def report_error(self):
        """Decrease current limit by one"""
        if not self._synced:
            return

        new_limit = 1
        self._change_limit(new_limit)

    async def report_success(self):
        """Increase current limit by one in case it has been decreased previously"""
        if not self._synced:
            return

        new_limit = min(self._max_limit, self._sp.limit + 1)
        self._change_limit(new_limit)

    async def acquire(self):
        async with self._lock:
            if not self._synced:
                self._synced = True

                response = await self._handler()
                while response.remaining <= 0:
                    self._logger.warning(
                        "You can't send more requests due to the API concurrency limit. "
                        "There is another running process (probably). "
                        f"Retrying in {self.limit_block_recheck_internal_ms} ms."
                    )
                    await asyncio.sleep(self.limit_block_recheck_internal_ms / 1000)
                    response = await self._handler()

                self._max_limit = response.limit
                self._change_limit(response.remaining)

        await self._sp.acquire()
        return True

    def release(self):
        self._sp.release()
