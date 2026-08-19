import asyncio

import httpx

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
        client = HttpClientAdapter()
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


def test_open_and_close_are_idempotent():

    # Arrange
    async def scenario():
        client = HttpClientAdapter(
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
