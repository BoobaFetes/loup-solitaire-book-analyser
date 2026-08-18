from ports.http import HttpClientBase


class FakeHttpClient(HttpClientBase[object]):
    def __init__(
        self,
        text_by_endpoint: dict[str, str] | None = None,
        *,
        json_by_endpoint: dict[str, dict[str, object]] | None = None,
        image_by_endpoint: dict[str, bytes] | None = None,
        default_content: bytes = b"fake-image",
    ) -> None:
        self.json_by_endpoint = json_by_endpoint or {}
        self.text_by_endpoint = text_by_endpoint or {}
        self.image_by_endpoint = image_by_endpoint or {}
        self.default_content = default_content
        self.json_requests: list[tuple[str, dict[str, str] | None]] = []
        self.text_requests: list[tuple[str, dict[str, str] | None]] = []
        self.image_requests: list[str] = []
        self.cache_enabled = True
        self.opened = False

    async def open(self, **kwargs) -> None:
        self.opened = True

    async def close(self) -> None:
        self.opened = False

    def enable_cache(self, enabled: bool = True) -> bool:
        previous_value = self.cache_enabled
        self.cache_enabled = enabled
        return previous_value

    async def get_json(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        self.json_requests.append((endpoint, headers))
        return self.json_by_endpoint.get(endpoint, {})

    async def get_text(
        self,
        endpoint: str,
        encoding: str | None = None,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> str:
        self.text_requests.append((endpoint, headers))
        return self.text_by_endpoint.get(endpoint, "")

    async def get_image(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        self.image_requests.append(endpoint)
        return self.image_by_endpoint.get(endpoint, self.default_content)
