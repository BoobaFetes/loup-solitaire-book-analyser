import asyncio

import httpx
import pytest

from adapters.cache import InMemoryCacheAdapter
from adapters.http.HttpClientAdapter import HttpClientAdapter
from ports.cache import CacheStoredValue


class _FakeEnabledCache:
    def __init__(
        self, cached_value: CacheStoredValue | None = None, enabled: bool = True
    ):
        self.cached_value = cached_value
        self.enabled = enabled
        self.get_calls = 0
        self.set_background_calls = 0

    def is_enabled(self) -> bool:
        return self.enabled

    def clear(self) -> None:
        self.cached_value = None

    def get(self, key: str) -> CacheStoredValue | None:
        self.get_calls += 1
        return self.cached_value

    async def set(
        self, key: str, value: CacheStoredValue, encoding: str | None = None
    ) -> None:
        self.cached_value = value

    def set_background(
        self, key: str, value: CacheStoredValue, encoding: str | None = None
    ) -> None:
        self.set_background_calls += 1
        self.cached_value = value

    async def flush(self) -> None:
        return None


def test_get_json_text_and_image_use_configured_async_client():
    async def scenario():
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/json":
                return httpx.Response(200, json={"name": "Loup Solitaire"})
            if request.url.path == "/text":
                return httpx.Response(200, text="texte")
            return httpx.Response(200, content=b"image")

        client = HttpClientAdapter(
            inmemory_cache=InMemoryCacheAdapter(),
            transport=httpx.MockTransport(handler),
            base_url="https://example.test",
        )
        await client.open()

        json_result = await client.get_json("/json")
        text_result = await client.get_text("/text")
        image_result = await client.get_image("/content")

        await client.close()
        return json_result, text_result, image_result

    assert asyncio.run(scenario()) == (
        {"name": "Loup Solitaire"},
        "texte",
        b"image",
    )


def test_get_text_decodes_with_requested_encoding():
    async def scenario():
        response = httpx.Response(200, content="épreuve".encode("cp1252"))
        client = HttpClientAdapter(
            inmemory_cache=InMemoryCacheAdapter(),
            transport=httpx.MockTransport(lambda request: response),
            base_url="https://example.test",
        )
        await client.open()
        result = await client.get_text("/", encoding="cp1252")
        await client.close()
        return result

    assert asyncio.run(scenario()) == "épreuve"


def test_get_raises_when_client_is_not_open():
    async def scenario():
        client = HttpClientAdapter(
            inmemory_cache=InMemoryCacheAdapter(),
        )
        try:
            await client.get_text("https://example.test")
        except RuntimeError as error:
            return str(error)
        return ""

    assert asyncio.run(scenario()) == "HTTP client is not open"


def test_enable_cache_false_bypasses_cache_reads_and_writes():
    async def scenario():
        cache = _FakeEnabledCache(cached_value="cached")
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, text="fresh")
            ),
            base_url="https://example.test",
        )

        await client.open()
        previous_cache_state = client.enable_cache(False)
        result = await client.get_text("/")
        await client.close()

        return (
            previous_cache_state,
            result,
            cache.get_calls,
            cache.set_background_calls,
        )

    assert asyncio.run(scenario()) == (True, "fresh", 0, 0)


@pytest.mark.parametrize(
    ("cache_adapter_enabled", "requested_state", "expected_result"),
    [
        (True, True, "cached"),
        (True, False, "fresh"),
        (False, True, "fresh"),
        (False, False, "fresh"),
    ],
)
def test_enable_cache_respects_requested_state_and_cache_adapter_availability(
    cache_adapter_enabled: bool, requested_state: bool, expected_result: str
):
    async def scenario():
        cache = _FakeEnabledCache(cached_value="cached", enabled=cache_adapter_enabled)
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, text="fresh")
            ),
            base_url="https://example.test",
        )

        await client.open()
        client.enable_cache(requested_state)
        result = await client.get_text("/")
        await client.close()

        return result

    assert asyncio.run(scenario()) == expected_result


def test_restore_cache_state_reenables_cache_only_when_cache_adapter_is_available():
    async def scenario(cache_adapter_enabled: bool):
        cache = _FakeEnabledCache(cached_value="cached", enabled=cache_adapter_enabled)
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, text="fresh")
            ),
            base_url="https://example.test",
        )

        await client.open()
        previous_cache_state = client.enable_cache(False)
        client.enable_cache(previous_cache_state)
        result = await client.get_text("/")
        await client.close()

        return previous_cache_state, result

    assert asyncio.run(scenario(cache_adapter_enabled=True)) == (True, "cached")
    assert asyncio.run(scenario(cache_adapter_enabled=False)) == (False, "fresh")
