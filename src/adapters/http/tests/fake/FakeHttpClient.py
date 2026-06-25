from ports.http import HttpClientBase


class FakeHttpClient(HttpClientBase[object]):
    def __init__(
        self,
        text_by_endpoint: dict[str, str] | None = None,
        *,
        json_by_endpoint: dict[str, dict[str, object]] | None = None,
        content_by_endpoint: dict[str, bytes] | None = None,
        default_content: bytes = b"fake-image",
    ) -> None:
        self.json_by_endpoint = json_by_endpoint or {}
        self.text_by_endpoint = text_by_endpoint or {}
        self.content_by_endpoint = content_by_endpoint or {}
        self.default_content = default_content
        self.content_requests: list[str] = []
        self.opened = False

    async def open(self, **kwargs) -> None:
        self.opened = True

    async def close(self) -> None:
        self.opened = False

    async def get_json(self, endpoint: str, retry: int = 3) -> dict[str, object]:
        return self.json_by_endpoint.get(endpoint, {})

    async def get_text(
        self, endpoint: str, encoding: str | None = None, retry: int = 3
    ) -> str:
        return self.text_by_endpoint.get(endpoint, "")

    async def get_content(self, endpoint: str, retry: int = 3) -> bytes:
        self.content_requests.append(endpoint)
        return self.content_by_endpoint.get(endpoint, self.default_content)
