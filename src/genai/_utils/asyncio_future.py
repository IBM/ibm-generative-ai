import sys
from asyncio import Lock, Semaphore, get_running_loop


class _LoopPlaceholder:
    pass


__all__ = ["AsyncioLock", "AsyncioSemaphore"]


class _AsyncioLoopMixin:
    """
    In asyncio prior Python 3.10 the loop being set directly in the constructor.
    Mentioned behaviour is not therefore compatible with our 'SharedEventLoop' approach.
    This class solves that by setting loop once actually needed and not inside the constructor itself.
    """

    _loop = None

    def _get_loop(self):
        if isinstance(self._loop, _LoopPlaceholder):
            self._loop = None

        loop = get_running_loop()

        if self._loop is None:
            self._loop = loop

        if loop is not self._loop:
            raise RuntimeError(f"{self!r} is bound to a different event loop")

        return loop

    def _fix_loop(self):
        if isinstance(self._loop, _LoopPlaceholder) or self._loop is None:
            self._loop = self._get_loop()

    async def acquire(self, *args, **kwargs):
        self._fix_loop()
        await super().acquire(*args, **kwargs)  # type: ignore

    def __init__(self, *args, **kwargs):
        if kwargs.get("loop", None) is None:
            kwargs["loop"] = _LoopPlaceholder()

        super().__init__(*args, **kwargs)


if sys.version_info < (3, 10, 0):

    class AsyncioLock(_AsyncioLoopMixin, Lock):
        pass

    class AsyncioSemaphore(_AsyncioLoopMixin, Semaphore):
        pass


else:
    AsyncioLock = Lock
    AsyncioSemaphore = Semaphore
