from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeNonOfficialBookListFinder(SpyStubFake):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.html = html

    def stub_urls(self, returned: list[str]) -> None:
        self._stub("urls", returned)

    @property
    def spy_urls(self) -> list[SpyCall]:
        return self._spy("urls")

    def urls(self, base_url: str) -> list[str]:
        returned = self._returned_or_default(
            "urls", [f"{base_url}book-1.html", f"{base_url}book-2.html"]
        )
        return self._record_call("urls", (base_url,), {}, returned)
