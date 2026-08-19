import asyncio
import hashlib
import logging
from pathlib import Path

from ports.cache import CacheStoredValue, InMemoryCacheInterface
from ports.os.IFileSystem import IFileSystem


class InMemoryCacheAdapter(InMemoryCacheInterface):
    def __init__(self, fs: IFileSystem, cache_dir: str, enabled: bool = False):
        self.enabled = enabled
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__cache: dict[str, CacheStoredValue] = {}
        self.__pending_writes: set[asyncio.Task[None]] = set()
        self.__fs: IFileSystem = fs
        self.__cache_dir = cache_dir
        self.__cache_path = self.__fs.get_path(cache_dir)
        if self.enabled and not self.__fs:
            raise ValueError(
                "InMemoryCacheAdapter requires a file system when enabled."
            )
        # If the cache is disabled, current cache files are deleted
        if not self.enabled:
            self.clear()
        self.__load()

    def __load(self) -> None:
        """Load existing cache files from disk into memory.

        The cache directory is created if it does not exist yet. Every file
        found under this directory is read and stored in memory. Files already
        using the ".cache" extension are indexed by their hash filename stem;
        older files are also indexed through the hash of their filename so they
        can still be found through get().
        """
        if not self.enabled:
            self.__logger.info("In-memory cache is disabled.")
            return

        if not self.__fs.is_dir_exists(self.__cache_dir):
            raise ValueError(
                f"In-memory cache directory '{self.__cache_path}' does not exist."
            )

        self.__logger.info(
            f"In-memory cache is enabled, loading the cache from {self.__cache_path}."
        )
        for file_path in self.__fs.list_files(self.__cache_dir, "*.cache"):
            internal_key = self.__to_internal_key_from_cache_file(file_path)
            value = (
                self.__fs.read_bytes(str(file_path))
                if file_path.name.endswith(".bin.cache")
                else self.__fs.read_file(str(file_path))
            )
            self.__cache[internal_key] = value

    def is_enabled(self) -> bool:
        return self.enabled

    def clear(self) -> None:
        """Clear the in-memory cache and delete all persisted files."""
        self.__cache.clear()
        self.__fs.clear(self.__cache_dir, "*.cache")

    def get(self, key: str) -> CacheStoredValue | None:
        if not self.enabled:
            return None

        internal_key = self.__to_internal_key(key)
        return self.__cache[internal_key] if internal_key in self.__cache else None

    async def set(self, key: str, value: CacheStoredValue) -> None:
        if not self.enabled:
            return

        internal_key = self.__to_internal_key(key)
        self.__cache[internal_key] = value
        file_path = self.__cache_path / self.__to_cache_filename(internal_key, value)
        if isinstance(value, bytes):
            await asyncio.to_thread(self.__fs.write_bytes, str(file_path), value)
            return

        await asyncio.to_thread(self.__fs.write_file, str(file_path), value)

    def set_background(self, key: str, value: CacheStoredValue) -> None:
        if not self.enabled:
            return

        task = asyncio.create_task(self.set(key, value))
        self.__pending_writes.add(task)
        task.add_done_callback(self.__discard_successful_write)

    async def flush(self) -> None:
        if not self.enabled:
            return

        if self.__pending_writes:
            await asyncio.gather(*tuple(self.__pending_writes))

    def __to_internal_key(self, key: str) -> str:
        """Convert any public cache key into a stable fixed-length key.

        Public keys may be URLs, file paths, or arbitrary strings of any length.
        SHA-256 is deterministic, so the same input key always produces the same
        internal key, and the hexadecimal digest is safe to use in file names.
        """
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def __to_cache_filename(self, internal_key: str, value: CacheStoredValue) -> str:
        """Build the filename used to persist an internal cache key on disk.

        The internal key is already a hash, so only a fixed extension is added
        to make generated cache files easy to identify in src/captures. The
        filename also keeps the stored value type so load() can read text and
        binary values with the right file mode.
        """
        suffix = "bin" if isinstance(value, bytes) else "txt"
        return f"{internal_key}.{suffix}.cache"

    def __to_internal_key_from_cache_file(self, file_path: Path) -> str:
        """Extract the internal key from a persisted cache filename.

        New cache files use "<hash>.txt.cache" or "<hash>.bin.cache". Older
        files may still use "<hash>.cache", so this method accepts both formats.
        """
        name = file_path.name
        if name.endswith(".txt.cache") or name.endswith(".bin.cache"):
            return name.removesuffix(".txt.cache").removesuffix(".bin.cache")

        return file_path.stem

    def __discard_successful_write(self, task: asyncio.Task[None]) -> None:
        """Remove a completed background write only when it succeeded.

        Failed or cancelled tasks stay in the pending set so flush() can still
        observe them later and surface the failure to the caller. Successful
        tasks can be discarded immediately because their file write is complete.
        """
        if task.cancelled():
            return

        if task.exception() is not None:
            return

        self.__pending_writes.discard(task)
