import asyncio

import httpx
import pytest

from adapters.cache.tests.fake import FakeInMemoryCache
from adapters.http.HttpClientAdapter import HttpClientAdapter


def test_get_json_text_and_image_use_configured_async_client(tmp_path):

    # Arrange
    async def scenario():
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/json":
                return httpx.Response(200, json={"name": "Loup Solitaire"})
            if request.url.path == "/text":
                return httpx.Response(200, text="texte")
            return httpx.Response(200, content=b"image")

        client = HttpClientAdapter(
            inmemory_cache=FakeInMemoryCache(enabled=False),
            transport=httpx.MockTransport(handler),
            base_url="https://example.test",
        )
        await client.open()

        json_result = await client.get_json("/json")
        text_result = await client.get_text("/text")
        image_result = await client.get_image("/content")

        await client.close()
        return json_result, text_result, image_result

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (
        {"name": "Loup Solitaire"},
        "texte",
        b"image",
    )
    assert actual == expected


def test_get_text_decodes_with_requested_encoding(tmp_path):

    # Arrange
    async def scenario():
        response = httpx.Response(200, content="épreuve".encode("cp1252"))
        client = HttpClientAdapter(
            inmemory_cache=FakeInMemoryCache(enabled=False),
            transport=httpx.MockTransport(lambda request: response),
            base_url="https://example.test",
        )
        await client.open()
        actual = await client.get_text("/", encoding="cp1252")
        await client.close()
        return actual

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = "épreuve"
    assert actual == expected


def test_get_raises_when_client_is_not_open(tmp_path):

    # Arrange
    async def scenario():
        client = HttpClientAdapter(
            inmemory_cache=FakeInMemoryCache(enabled=False),
        )
        try:
            await client.get_text("https://example.test")
        except RuntimeError as error:
            return str(error)
        return ""

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = "HTTP client is not open"
    assert actual == expected


def test_enable_cache_false_bypasses_cache_reads_and_writes():

    # Arrange
    async def scenario():
        cache = FakeInMemoryCache(cached_value="cached")
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, text="fresh")
            ),
            base_url="https://example.test",
        )

        await client.open()
        previous_cache_state = client.enable_cache(False)
        actual = await client.get_text("/")
        await client.close()

        return (
            previous_cache_state,
            actual,
            cache.get_calls,
            cache.set_background_calls,
        )

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (True, "fresh", 0, 0)
    assert actual == expected


def test_get_image_bypasses_cache_even_when_cache_is_enabled():

    # Arrange
    async def scenario():
        cache = FakeInMemoryCache(cached_value=b"cached-image")
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content=b"fresh-image")
            ),
            base_url="https://example.test",
        )

        await client.open()
        actual = await client.get_image("/")
        await client.close()

        return actual, cache.get_calls, cache.set_background_calls, cache.cached_value

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (b"fresh-image", 0, 0, b"cached-image")
    assert actual == expected


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
    # Arrange
    async def scenario():
        cache = FakeInMemoryCache(cached_value="cached", enabled=cache_adapter_enabled)
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, text="fresh")
            ),
            base_url="https://example.test",
        )

        await client.open()
        client.enable_cache(requested_state)
        actual = await client.get_text("/")
        await client.close()

        return actual

    # Act
    actual = asyncio.run(scenario())

    # Assert
    assert actual == expected_result


def test_restore_cache_state_reenables_cache_only_when_cache_adapter_is_available():

    # Arrange
    async def scenario(cache_adapter_enabled: bool):
        cache = FakeInMemoryCache(cached_value="cached", enabled=cache_adapter_enabled)
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
        actual = await client.get_text("/")
        await client.close()

        return previous_cache_state, actual

    # Act
    actual = asyncio.run(scenario(cache_adapter_enabled=True))

    # Assert
    expected = (True, "cached")
    assert actual == expected
    actual = asyncio.run(scenario(cache_adapter_enabled=False))

    expected = (False, "fresh")
    assert actual == expected


def test_open_and_close_are_idempotent():

    # Arrange
    async def scenario():
        client = HttpClientAdapter(
            inmemory_cache=FakeInMemoryCache(enabled=False),
            transport=httpx.MockTransport(lambda request: httpx.Response(200)),
            base_url="https://example.test",
        )

        await client.open()
        await client.open()
        await client.close()
        await client.close()

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = None
    assert actual is expected


def test_get_json_uses_valid_cache_without_http_call():

    # Arrange
    async def scenario():
        cache = FakeInMemoryCache(cached_value='{"cached": true}')
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(500, text="should not be called")
            ),
            base_url="https://example.test",
        )

        await client.open()
        actual = await client.get_json("/")
        await client.close()

        return actual, cache.get_calls, cache.set_background_calls

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = ({"cached": True}, 1, 0)
    assert actual == expected


def test_get_json_ignores_invalid_cache_then_refreshes_it():

    # Arrange
    async def scenario():
        cache = FakeInMemoryCache(cached_value="{invalid")
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"fresh": True})
            ),
            base_url="https://example.test",
        )

        await client.open()
        actual = await client.get_json("/")
        await client.close()

        return actual, cache.get_calls, cache.set_background_calls, cache.cached_value

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (
        {"fresh": True},
        1,
        1,
        '{"fresh": true}',
    )
    assert actual == expected


def test_get_text_reads_from_cache_without_http_call():

    # Arrange
    async def scenario():
        cache = FakeInMemoryCache(cached_value="cached-text")
        client = HttpClientAdapter(
            inmemory_cache=cache,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(500, text="should not be called")
            ),
            base_url="https://example.test",
        )

        await client.open()
        actual = await client.get_text("/")
        await client.close()

        return actual, cache.get_calls, cache.set_background_calls

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = ("cached-text", 1, 0)
    assert actual == expected


def test_get_text_retries_after_connect_error():

    # Arrange
    async def scenario():
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise httpx.ConnectError("temporary failure", request=request)
            return httpx.Response(200, text="fresh")

        client = HttpClientAdapter(
            inmemory_cache=FakeInMemoryCache(enabled=False),
            retry_delay=0,
            transport=httpx.MockTransport(handler),
            base_url="https://example.test",
        )

        await client.open()
        actual = await client.get_text("/", retry=1)
        await client.close()

        return actual, calls

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = ("fresh", 2)
    assert actual == expected


def test_get_text_raises_http_status_error():

    # Arrange
    async def scenario():
        client = HttpClientAdapter(
            inmemory_cache=FakeInMemoryCache(enabled=False),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(500, request=request, text="boom")
            ),
            base_url="https://example.test",
        )

        await client.open()
        try:
            await client.get_text("/", retry=0)
        except httpx.HTTPStatusError as error:
            await client.close()
            return error.response.status_code
        return 0

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = 500
    assert actual == expected
