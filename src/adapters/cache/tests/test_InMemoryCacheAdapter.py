import asyncio
import hashlib

import pytest

from adapters.cache import InMemoryCacheAdapter
from adapters.os import FileSystemAdapter

CACHE_DIR = "caches"


def _digest(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def test_disabled_cache_ignores_reads_and_writes(tmp_path):

    # Arrange
    async def scenario():
        fs = FileSystemAdapter(str(tmp_path))
        cache = InMemoryCacheAdapter(fs, CACHE_DIR, enabled=False)

        await cache.set("key", "value")
        cache.set_background("key", "background")
        await cache.flush()

        return cache.is_enabled(), cache.get("key"), list(tmp_path.rglob("*.cache"))

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (False, None, [])
    assert actual == expected


def test_enabled_cache_requires_existing_cache_directory(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))

    # Act
    with pytest.raises(ValueError, match="does not exist"):
        InMemoryCacheAdapter(fs, CACHE_DIR, enabled=True)

    # Assert
    assert True


def test_set_persists_text_and_bytes_and_reload_reads_them(tmp_path):

    # Arrange
    async def scenario():
        fs = FileSystemAdapter(str(tmp_path))
        fs.create(CACHE_DIR)
        cache = InMemoryCacheAdapter(fs, CACHE_DIR, enabled=True)

        await cache.set("text-key", "texte")
        await cache.set("bytes-key", b"bytes")

        reloaded = InMemoryCacheAdapter(fs, CACHE_DIR, enabled=True)
        return (
            reloaded.get("text-key"),
            reloaded.get("bytes-key"),
            sorted(path.name for path in fs.list_files(CACHE_DIR, "*.cache")),
        )

    # Act
    text_file = f"{_digest('text-key')}.txt.cache"
    bytes_file = f"{_digest('bytes-key')}.bin.cache"
    actual = asyncio.run(scenario())

    # Assert
    expected = ("texte", b"bytes", sorted([text_file, bytes_file]))
    assert actual == expected


def test_load_accepts_legacy_cache_file_extension(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))
    fs.create(CACHE_DIR)
    legacy_key = _digest("legacy-key")
    fs.write_file(f"{CACHE_DIR}/{legacy_key}.cache", "legacy")

    cache = InMemoryCacheAdapter(fs, CACHE_DIR, enabled=True)

    # Act
    actual = cache.get("legacy-key")

    # Assert
    expected = "legacy"
    assert actual == expected


def test_set_background_flushes_pending_write(tmp_path):

    # Arrange
    async def scenario():
        fs = FileSystemAdapter(str(tmp_path))
        fs.create(CACHE_DIR)
        cache = InMemoryCacheAdapter(fs, CACHE_DIR, enabled=True)

        cache.set_background("key", "value")
        await cache.flush()

        return cache.get("key"), fs.read_file(f"{CACHE_DIR}/{_digest('key')}.txt.cache")

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = ("value", "value")
    assert actual == expected


async def scenario_removes_memory_and_persisted_cache_files(tmp_path, enabled: bool):
    fs = FileSystemAdapter(str(tmp_path))
    fs.create(CACHE_DIR)
    cache = InMemoryCacheAdapter(fs, CACHE_DIR, enabled=enabled)
    await cache.set("key", "value")

    cache.clear()

    return cache.get("key"), fs.list_files(CACHE_DIR, "*.cache")


def test_clear_removes_memory_and_persisted_cache_files_when_enabled(tmp_path):

    # Arrange
    async def scenario():
        return await scenario_removes_memory_and_persisted_cache_files(
            tmp_path, enabled=True
        )

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (None, [])
    assert actual == expected


def test_clear_removes_memory_and_persisted_cache_files_when_disabled(tmp_path):

    # Arrange
    async def scenario():
        return await scenario_removes_memory_and_persisted_cache_files(
            tmp_path, enabled=False
        )

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (None, [])
    assert actual == expected
