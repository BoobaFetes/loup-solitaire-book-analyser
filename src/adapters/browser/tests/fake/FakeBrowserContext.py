from adapters.browser.tests.fake.FakeBrowserPage import FakeBrowserPage
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeBrowserContext(SpyStubFake):
    def __init__(self) -> None:
        super().__init__()
        self.pages: list[FakeBrowserPage] = []

    def stub_new_page(self, returned: FakeBrowserPage) -> None:
        self._stub("new_page", returned)

    @property
    def spy_new_page(self) -> list[SpyCall]:
        return self._spy("new_page")

    async def new_page(self) -> FakeBrowserPage:
        page = FakeBrowserPage()
        self.pages.append(page)
        returned = self._returned_or_default("new_page", page)
        return self._record_call("new_page", (), {}, returned)
