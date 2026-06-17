import asyncio

import httpx

from adapters.http.HttpClientAdapter import HttpClientAdapter


def test_get_json_text_and_content_use_configured_async_client():
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
        content_result = await client.get_content("/content")

        await client.close()
        return json_result, text_result, content_result

    assert asyncio.run(scenario()) == (
        {"name": "Loup Solitaire"},
        "texte",
        b"image",
    )


def test_get_text_decodes_with_requested_encoding():
    async def scenario():
        response = httpx.Response(200, content="épreuve".encode("cp1252"))
        client = HttpClientAdapter(
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
        client = HttpClientAdapter()
        try:
            await client.get_text("https://example.test")
        except RuntimeError as error:
            return str(error)
        return ""

    assert asyncio.run(scenario()) == "HTTP client is not open"
