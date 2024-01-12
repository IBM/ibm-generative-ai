from genai._utils.limiters.adjustable_semaphor import AdjustableAsyncSemaphore
from genai._utils.limiters.base_limiter import BaseLimiter


class LocalLimiter(BaseLimiter):
    """
    A class for limiting the concurrency of certain operations locally with dynamic limit based on report loop feedback
    """

    def __init__(self, limit: int):
        assert limit > 0
        self._max_limit = limit
        self._sp = AdjustableAsyncSemaphore(limit)

    async def acquire(self):
        await self._sp.acquire()
        return True

    def release(self):
        self._sp.release()

    async def report_error(self):
        """Reports an error to the limiter, reducing the current limit by 1 if it is greater than 1."""
        current_limit = self._sp.limit
        if current_limit > 1:
            self._sp.change_max_limit(current_limit - 1)

    async def report_success(self):
        """Reports a successful operation to the limiter, increasing the current limit by 1, up to the maximum limit."""
        new_limit = min(self._max_limit, self._sp.limit + 1)
        self._sp.change_max_limit(new_limit)
