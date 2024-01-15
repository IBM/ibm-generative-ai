from queue import Queue
from typing import Generic, Optional, TypeVar

Order = int
T = TypeVar("T", bound=tuple[Order, ...])


class OrderedQueue(Queue, Generic[T]):
    """
    Special queue which ensures that items are processed in linear fashion (1, 2, 3, ...)
    The order parameter is specified as first item of the tuple.
    """

    def __init__(self, maxsize: int = 0, start: int = 0):
        super().__init__(maxsize)
        self.queue: dict[int, T] = {}
        self._expected_idx = start
        self._current_idx = start

    def put(self, item: T, block: bool = True, timeout: Optional[float] = None) -> None:
        if item[0] is None:
            return self.put((self._expected_idx, *item[1:]), block, timeout)

        super().put(item, block, timeout)

    def flush(self) -> None:
        """
        Flushes all the items in the queue (does not wait for the consumer).
        """
        while not self.empty():
            self.queue.popitem()
            self.task_done()

    def get(self, block=True, timeout=None) -> T:
        """
        Get an item from the queue (waits until someone adds the item to the queue with given index)

        Args:
            block (bool): Indicates whether the method should block until an item is available in the queue.
            timeout (Optional[float]): The maximum amount of time (in seconds) that the method should wait.

        Returns:
            T: The item retrieved from the queue.

        """
        with self.not_empty:
            target = self._current_idx
            self._current_idx += 1

            item = self.not_empty.wait_for(
                lambda: self._get() if target == self._expected_idx and target in self.queue else None
            )
            assert item

            self._expected_idx += 1
            self.not_full.notify()
            if not self._qsize():
                self.not_empty.notify_all()

            return item

    def _get(self) -> T:
        return self.queue.pop(self._expected_idx)

    def _put(self, item: T):
        idx: Order = item[0]
        if idx in self.queue:
            raise ValueError(f"Entry with key '{idx}' already exists!")
        self.queue[idx] = item

    def _init(self, maxsize: int):
        self.queue = {}
