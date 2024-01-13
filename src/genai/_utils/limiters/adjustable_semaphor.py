import asyncio
import sys
from asyncio import Future
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

        # Note: not used in Python < 3.10 due to different Semaphore implementation
        self._dummy_waiters: set[Future] = set()

    @property
    def limit(self):
        return self._max_limit

    @property
    def processing(self):
        return self._max_limit - self._value

    @property
    def waiting(self):
        if self._waiters is None:
            return 0

        if sys.version_info < (3, 10, 0):
            return len(self._waiters)

        return len(self._waiters) - len(self._dummy_waiters)

    def change_max_limit(self, new_limit: int) -> bool:
        """
        Change the maximum limit of the semaphore.

        Args:
            new_limit (int): The new maximum limit for the semaphore.

        Returns:
            bool: Returns `True` if the maximum limit was changed, `False` otherwise.

        Raises:
            ValueError: If `new_limit` is less than 1.
        """
        if new_limit < 1:
            raise ValueError("Semaphore concurrency cannot be less than 1!")

        if new_limit == self._max_limit:
            return False

        old_limit = self._max_limit
        self._max_limit = new_limit
        running = old_limit - self._value

        if new_limit > old_limit:
            points_to_add = new_limit - running
            for _ in range(0, points_to_add):
                self.release()
        else:
            points_to_remove = running - new_limit

            for _ in range(0, points_to_remove):
                if self._value == 0 or self._waiters:
                    fut: asyncio.Future = self._loop.create_future()

                    def handle_done(f: Future):
                        assert f.done()

                        with suppress(ValueError):
                            self._waiters.remove(f)
                        with suppress(KeyError):
                            self._dummy_waiters.remove(f)

                        if self._value > 0:
                            # because it gets immediately incremented in release() method
                            self._value -= 1
                            self.release()

                    fut.add_done_callback(handle_done)

                    self._dummy_waiters.add(fut)
                    self._waiters.appendleft(fut)
                else:
                    self._value -= 1

        return True
