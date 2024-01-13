from typing import Awaitable, Callable

from pydantic import BaseModel, Field

from genai._utils.asyncio_future import AsyncioLock
from genai._utils.limiters.adjustable_semaphor import AdjustableAsyncSemaphore
from genai._utils.limiters.base_limiter import BaseLimiter


class ConcurrencyResponse(BaseModel):
    limit: int = Field(..., ge=1, description="Maximum number of concurrent requests")
    remaining: int = Field(..., ge=0, description="Number of remaining requests before reaching the limit")


ExternalLimiterHandler = Callable[[], Awaitable[ConcurrencyResponse]]


class ExternalLimiter(BaseLimiter):
    """A limiter class that interacts with an external handler to enforce dynamic concurrent limits."""

    def __init__(self, *, handler: ExternalLimiterHandler):
        self._handler = handler
        self._lock = AsyncioLock()
        self._sp = AdjustableAsyncSemaphore(0)
        self._last_retrieved_limit = 0
        self._synced = False

    async def report_error(self):
        """
        Decrease current limit by one (if possible)
        """
        limit_has_changed = await self.resync()
        current_limit = self._sp.limit
        if not limit_has_changed and current_limit > 1:
            self._sp.change_max_limit(current_limit - 1)

    async def report_success(self):
        """
        Increase current limit by one in case it has been decreased previously
        """
        new_limit = min(self._last_retrieved_limit, self._sp.limit + 1)
        self._sp.change_max_limit(new_limit)

    async def resync(self) -> bool:
        """
        Asynchronously resynchronizes the limit by calling provided handler.
        """
        response = await self._handler()
        limit_has_changed = self._sp.change_max_limit(response.limit)
        if limit_has_changed:
            self._last_retrieved_limit = response.limit

        return limit_has_changed

    async def acquire(self):
        async with self._lock:
            if not self._synced:
                await self.resync()
                self._synced = True

        await self._sp.acquire()
        return True

    def release(self):
        self._sp.release()
