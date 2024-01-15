from genai._utils.limiters.base_limiter import BaseLimiter


class DummyLimiter(BaseLimiter):
    async def acquire(self):
        return True

    def release(self):
        return
