from abc import abstractmethod
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class SharedResource(Generic[T], AbstractContextManager):
    """Class representing a shared resource.

    This class provides a way to manage a shared resource using the context manager protocol.
    It keeps track of the number of references to the resource and initializes it when the first
    reference is made. The resource is released when the last reference is closed.
    """

    def __init__(self):
        self._ref_count = 0
        self._resource: Optional[T] = None

    @abstractmethod
    def _enter(self) -> T:
        """
        Create a new resource (called when the first reference is made)

        Returns:
            T: new resource
        """
        raise NotImplementedError

    @abstractmethod
    def _exit(self) -> None:
        """
        Destroys an existing resource (called when there is not a reference to the resource)
        """
        raise NotImplementedError

    def __enter__(self) -> T:
        self._ref_count += 1
        if self._ref_count == 1:
            self._resource = self._enter()

        assert self._resource
        return self._resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ref_count -= 1
        if self._ref_count == 0:
            self._exit()
            self._resource = None


class AsyncSharedResource(Generic[T], AbstractAsyncContextManager):
    def __init__(self):
        self._ref_count = 0
        self._resource: Optional[T] = None

    @abstractmethod
    async def _enter(self) -> T:
        """
        Create a new resource (called when the first reference is made)

        Returns:
            T: new resource
        """
        raise NotImplementedError

    @abstractmethod
    async def _exit(self) -> T:
        """
        Destroys an existing resource (called when there is not a reference to the resource)
        """
        raise NotImplementedError

    async def __aenter__(self) -> T:
        self._ref_count += 1
        if self._ref_count == 1:
            self._resource = await self._enter()

        assert self._resource
        return self._resource

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._ref_count -= 1
        if self._ref_count == 0:
            await self._exit()
            self._resource = None
