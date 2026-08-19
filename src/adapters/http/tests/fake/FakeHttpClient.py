from ports.http import HttpClientBase
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeHttpClient(HttpClientBase[object], SpyStubFake):
    def __init__(
        self,
        text_by_endpoint: dict[str, str] | None = None,
        *,
        json_by_endpoint: dict[str, dict[str, object]] | None = None,
        image_by_endpoint: dict[str, bytes] | None = None,
        default_content: bytes = b"fake-image",
    ) -> None:
        SpyStubFake.__init__(self)
        self.json_by_endpoint = json_by_endpoint or {}
        self.text_by_endpoint = text_by_endpoint or {}
        self.image_by_endpoint = image_by_endpoint or {}
        self.default_content = default_content
        self.json_requests: list[tuple[str, dict[str, str] | None]] = []
        self.text_requests: list[tuple[str, dict[str, str] | None]] = []
        self.image_requests: list[str] = []
        self.cache_enabled = True
        self.opened = False

    def stub_open(self, returned: None = None) -> None:
        self._stub("open", returned)

    @property
    def spy_open(self) -> list[SpyCall]:
        return self._spy("open")

    def stub_close(self, returned: None = None) -> None:
        self._stub("close", returned)

    @property
    def spy_close(self) -> list[SpyCall]:
        return self._spy("close")

    def stub_enable_cache(self, returned: bool) -> None:
        self._stub("enable_cache", returned)

    @property
    def spy_enable_cache(self) -> list[SpyCall]:
        return self._spy("enable_cache")

    def stub_get_json(
        self,
        returned: dict[str, object],
        *,
        endpoint: str | None = None,
    ) -> None:
        if endpoint is None:
            self._stub("get_json", returned)
        else:
            self.json_by_endpoint[endpoint] = returned

    @property
    def spy_get_json(self) -> list[SpyCall]:
        return self._spy("get_json")

    def stub_get_text(self, returned: str, *, endpoint: str | None = None) -> None:
        if endpoint is None:
            self._stub("get_text", returned)
        else:
            self.text_by_endpoint[endpoint] = returned

    @property
    def spy_get_text(self) -> list[SpyCall]:
        return self._spy("get_text")

    def stub_get_image(self, returned: bytes, *, endpoint: str | None = None) -> None:
        if endpoint is None:
            self._stub("get_image", returned)
        else:
            self.image_by_endpoint[endpoint] = returned

    @property
    def spy_get_image(self) -> list[SpyCall]:
        return self._spy("get_image")

    async def open(self, **kwargs) -> None:
        self.opened = True
        returned = self._returned_or_default("open", None)
        return self._record_call("open", (), kwargs, returned)

    async def close(self) -> None:
        self.opened = False
        returned = self._returned_or_default("close", None)
        return self._record_call("close", (), {}, returned)

    def enable_cache(self, enabled: bool = True) -> bool:
        previous_value = self.cache_enabled
        self.cache_enabled = enabled
        returned = self._returned_or_default("enable_cache", previous_value)
        return self._record_call("enable_cache", (enabled,), {}, returned)

    async def get_json(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        self.json_requests.append((endpoint, headers))
        returned = self._returned_or_default(
            "get_json", self.json_by_endpoint.get(endpoint, {})
        )
        return self._record_call(
            "get_json",
            (endpoint,),
            {"retry": retry, "headers": headers},
            returned,
        )

    async def get_text(
        self,
        endpoint: str,
        encoding: str | None = None,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> str:
        self.text_requests.append((endpoint, headers))
        returned = self._returned_or_default(
            "get_text", self.text_by_endpoint.get(endpoint, "")
        )
        return self._record_call(
            "get_text",
            (endpoint,),
            {"encoding": encoding, "retry": retry, "headers": headers},
            returned,
        )

    async def get_image(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        self.image_requests.append(endpoint)
        returned = self._returned_or_default(
            "get_image", self.image_by_endpoint.get(endpoint, self.default_content)
        )
        return self._record_call(
            "get_image",
            (endpoint,),
            {"retry": retry, "headers": headers},
            returned,
        )
