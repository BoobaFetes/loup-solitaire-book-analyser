from typing import Protocol, TypeAlias

CacheStoredValue: TypeAlias = str | bytes


class InMemoryCacheInterface(Protocol):
    """Interface for an in-memory cache backed by files.

    The cache keeps values immediately available in memory while allowing them
    to be persisted on disk. Implementations may write files asynchronously so
    callers can continue their work without blocking the event loop.
    """

    def is_enabled(self) -> bool:
        """Return whether the cache is enabled.
        Returns:
            True if the cache is enabled, False otherwise.
        """
        ...

    def clear(self) -> None:
        """Clear the in-memory cache and delete all persisted files.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        ...

    def get(self, key: str) -> CacheStoredValue | None:
        """Return the cached value for a key, if it exists.

        Args:
            key: Cache key or file path used to identify the cached content.

        Returns:
            The cached content, or None when the key is not available.
        """

        ...

    async def set(self, key: str, value: CacheStoredValue) -> None:
        """Store a value in memory and persist it before returning.

        Implementations should avoid blocking the event loop while writing the
        file, for example by offloading the synchronous file write to a worker
        thread. Once this coroutine has been awaited, the caller can consider
        the file write completed or failed with an exception.

        Args:
            key: Cache key or file path where the value must be persisted.
            value: Content to cache and write to disk.
        """

        ...

    def set_background(self, key: str, value: CacheStoredValue) -> None:
        """Schedule a cache write without waiting for disk persistence.

        This method should update the in-memory value immediately, then start
        the file write in the background. The write is not guaranteed to be
        finished when this method returns; callers must await flush() before
        shutdown when they need to guarantee that pending files are written.

        Args:
            key: Cache key or file path where the value must be persisted.
            value: Content to cache and write to disk.
        """

        ...

    async def flush(self) -> None:
        """Wait until all pending background writes are finished.

        Call this before closing the application or ending a workflow that used
        set_background(). If a background write failed, this coroutine should
        surface the exception so the caller knows persistence was not completed.
        """

        ...
