import asyncio
import threading
from asyncio import CancelledError
from contextlib import suppress
from typing import Callable, Optional

from genai._utils.shared_instance import SharedResource

__all__ = ["shared_event_loop"]


class _SharedEventLoop(SharedResource[asyncio.AbstractEventLoop]):
    """
    A class that manages a shared asyncio event loop.
    """

    def __init__(self):
        super().__init__()
        self._close_signal_handlers: list[Callable[[], None]] = []

    def _enter(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()

        def worker():
            asyncio.set_event_loop(loop)
            loop.run_forever()

            not_finished_tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
            # Tasks should be given time to run even if they are cancelled so they can do cleanup
            # https://xinhuang.github.io/posts/2017-07-31-common-mistakes-using-python3-asyncio.html
            for task in not_finished_tasks:
                with suppress(CancelledError):
                    loop.run_until_complete(task)

            loop.close()

        self._loop = loop
        self._thread = threading.Thread(target=worker)
        self._thread.start()

        return loop

    def add_close_handler(self, handler: Callable[[], None]) -> None:
        self._close_signal_handlers.append(handler)

    def remove_close_handler(self, handler: Callable[[], None]):
        if handler in self._close_signal_handlers:
            self._close_signal_handlers.remove(handler)

    def signal_emit_close(self):
        for handler in self._close_signal_handlers:
            handler()

    def _exit(self):
        self._close_signal_handlers.clear()
        self._loop.call_soon_threadsafe(lambda: self._loop.stop())
        self._thread.join()

    def get_running_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        return self._resource


shared_event_loop = _SharedEventLoop()


def handle_shutdown_event(*_args) -> None:
    """
    Handles the shutdown event.
    """
    shared_event_loop.signal_emit_close()
