from queue import Queue


class FlushableQueue(Queue):
    def flush(self):
        """
        Flushes the contents of the queue by removing all items.

        This method continuously removes items from the queue until it is empty. Each item is retrieved from the
        queue using the `get()` method, and then the `task_done()` method is called to indicate
        that the item has been processed.
        """
        while not self.empty():
            _ = self.get()
            self.task_done()
