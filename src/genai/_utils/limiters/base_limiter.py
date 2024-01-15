from abc import ABC, abstractmethod


class BaseLimiter(ABC):
    @abstractmethod
    async def acquire(self):
        ...

    @abstractmethod
    def release(self):
        ...

    async def report_error(self):  # noqa: B027 # empty body without being abstract
        pass

    async def report_success(self):  # noqa: B027 # empty body without being abstract
        pass

    async def __aenter__(self):
        await self.acquire()
        # We have no use for the "as ..."  clause in the with
        # statement for locks.
        return None

    async def __aexit__(self, exc_type, exc, tb):
        self.release()
