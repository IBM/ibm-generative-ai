import asyncio
from typing import Callable, Optional

from genai._utils.limiters.base_limiter import BaseLimiter


class LoopBoundLimiter(BaseLimiter):
    """
    A class that limits the frequency of executing a code block using a provided limiter.
    The limiter must be created inside an event loop.
    """

    _limiter: BaseLimiter
    _loop: Optional[asyncio.AbstractEventLoop] = None

    def __init__(self, factory: Callable[[], BaseLimiter]):
        self._factory = factory

    async def acquire(self):
        return await self._get_limiter().acquire()

    def release(self):
        return self._get_limiter().release()

    async def report_error(self):
        return await self._limiter.report_error()

    async def report_success(self):
        return await self._limiter.report_success()

    def _get_limiter(self) -> BaseLimiter:
        loop = asyncio.get_running_loop()
        if loop is not self._loop:
            self._limiter = self._factory()
            self._loop = loop
        return self._limiter
