import asyncio
from typing import Optional

from genai._utils.asyncio_future import AsyncioLock
from genai._utils.limiters.base_limiter import BaseLimiter


class LimiterContainer(BaseLimiter):
    """
    A class that represents a container for multiple limiters.
    """

    def __init__(self, *limiters: Optional[BaseLimiter]):
        self._limiters = [limiter for limiter in limiters if limiter]
        self._lock = AsyncioLock()

    async def acquire(self):
        """
        Acquires all the limiters in parallel.

        If there are no limiters available, this method will return True.
        If there is only one limiter available, it will be acquired and the method will return True.
        If there are multiple limiters available, they will be acquired in parallel using asyncio.gather().

        Returns:
            True: If all limiters are acquired successfully.

        Example::
            limiter_group = LimiterGroup()
            await limiter_group.acquire()
        """
        if len(self._limiters) == 0:
            return True

        if len(self._limiters) == 1:
            await self._limiters[0].acquire()
            return True

        async with self._lock:
            await asyncio.gather(*[limiter.acquire() for limiter in self._limiters])
            return True

    def release(self):
        """
        Release all limiters.
        """
        for limiter in self._limiters:
            limiter.release()

    async def report_error(self):
        """
        Report error to nested limiters.

        This method asynchronously reports any errors that occurred during execution.
        """
        await asyncio.gather(*[limiter.report_error() for limiter in self._limiters])

    async def report_success(self):
        """
        Report success to nested limiters.
        """
        await asyncio.gather(*[limiter.report_success() for limiter in self._limiters])
