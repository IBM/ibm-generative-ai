import asyncio
from asyncio import CancelledError, Future
from collections import deque
from contextlib import suppress

from genai._utils.asyncio_future import AsyncioSemaphore


class AdjustableAsyncSemaphore(AsyncioSemaphore):
    """
    AdjustableAsyncSemaphore is a subclass of Semaphore that allows for dynamic adjustment of its maximum limit.
    It includes methods for changing the maximum limit and getting information about the current state of the semaphore.
    """

    def __init__(self, value: int = 1):
        super().__init__(value)
        self._max_limit = value
        self._waiters = deque()
        self._processing = 0
        self._dummy_waiters: set[Future] = set()

    @property
    def limit(self):
        return self._max_limit

    @property
    def processing(self):
        return self._processing

    @property
    def waiting(self):
        if self._waiters is None:
            return 0

        return len(self._waiters) - len(self._dummy_waiters)

    async def acquire(self):
        """Taken from Python 3.11"""

        if not self.locked():
            self._value -= 1
            self._processing += 1
            return True

        fut = self._get_loop().create_future()
        self._waiters.append(fut)

        # Finally block should be called before the CancelledError
        # handling as we don't want CancelledError to call
        # _wake_up_first() and attempt to wake up itself.
        try:
            try:
                await fut
            finally:
                self._waiters.remove(fut)
        except CancelledError:
            if not fut.cancelled():
                self._value += 1
                self._processing -= 1
                self._wake_up_next()
            raise

        if self._value > 0:
            self._wake_up_next()
        return True

    def release(self):
        """Taken from Python 3.11"""
        self._value += 1
        self._processing -= 1
        self._wake_up_next()

    def _wake_up_next(self):
        """Taken from Python 3.11"""
        if not self._waiters:
            return

        for fut in self._waiters:
            if not fut.done():
                self._value -= 1
                if fut not in self._dummy_waiters:
                    self._processing += 1
                fut.set_result(True)
                return

    def change_max_limit(self, new_limit: int) -> bool:
        """
        Change the maximum limit of the semaphore.

        Args:
            new_limit (int): The new maximum limit for the semaphore.

        Returns:
            bool: Returns `True` if the maximum limit was changed, `False` otherwise.

        Raises:
            ValueError: If `new_limit` is less than 0.
        """
        if new_limit < 0:
            raise ValueError("Semaphore concurrency cannot be less than 0!")

        if new_limit == self._max_limit:
            return False

        old_limit = self._max_limit
        self._max_limit = new_limit

        if new_limit > old_limit:
            points_to_add = new_limit - old_limit
            for _ in range(0, points_to_add):
                self._processing += 1
                self.release()
        else:
            points_to_remove = old_limit - new_limit

            for _ in range(0, points_to_remove):
                if self.locked():
                    fut: asyncio.Future = self._get_loop().create_future()

                    def handle_done(f: Future):
                        assert f.done()

                        with suppress(ValueError):
                            self._waiters.remove(f)

                        if self._value > 0:
                            self._wake_up_next()

                        with suppress(KeyError):
                            self._dummy_waiters.remove(f)

                    fut.add_done_callback(handle_done)

                    self._dummy_waiters.add(fut)
                    self._waiters.appendleft(fut)
                else:
                    self._value -= 1

        return True
