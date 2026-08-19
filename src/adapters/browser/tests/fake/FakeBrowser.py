from typing import cast

from adapters.browser.tests.fake.FakeBrowserContext import FakeBrowserContext
from adapters.browser.tests.fake.FakePageHandler import FakePageHandler
from ports.browser import BrowserInterface, PageHandlerInterface
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeBrowser(BrowserInterface[object, object, object], SpyStubFake):
    def __init__(self, page_handler: FakePageHandler | None = None) -> None:
        super().__init__()
        SpyStubFake.__init__(self)
        self.page_handler = page_handler
        self.contexts = [FakeBrowserContext()]
        self.new_context_options: list[dict[str, object]] = []
        self.opened = False

    def stub_start(self, returned: None = None) -> None:
        self._stub("start", returned)

    @property
    def spy_start(self) -> list[SpyCall]:
        return self._spy("start")

    def stub_close(self, returned: None = None) -> None:
        self._stub("close", returned)

    @property
    def spy_close(self) -> list[SpyCall]:
        return self._spy("close")

    def stub_new_context(self, returned: int) -> None:
        self._stub("new_context", returned)

    @property
    def spy_new_context(self) -> list[SpyCall]:
        return self._spy("new_context")

    def stub_new_page(
        self, returned: PageHandlerInterface[object, object, object]
    ) -> None:
        self._stub("new_page", returned)

    @property
    def spy_new_page(self) -> list[SpyCall]:
        return self._spy("new_page")

    async def __aenter__(self) -> "FakeBrowser":
        self.opened = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.opened = False

    async def start(self) -> None:
        self.opened = True
        returned = self._returned_or_default("start", None)
        return self._record_call("start", (), {}, returned)

    async def close(self) -> None:
        self.opened = False
        returned = self._returned_or_default("close", None)
        return self._record_call("close", (), {}, returned)

    async def new_context(self, **kwargs) -> int:
        self.new_context_options.append(kwargs)
        self.contexts.append(FakeBrowserContext())
        returned = self._returned_or_default("new_context", len(self.contexts) - 1)
        return self._record_call("new_context", (), kwargs, returned)

    async def new_page(
        self, url: str, context_index: int = 0
    ) -> PageHandlerInterface[object, object, object]:
        if self.page_handler is None:
            self.page_handler = FakePageHandler(base_url=url)
        default = cast(PageHandlerInterface[object, object, object], self.page_handler)
        returned = self._returned_or_default("new_page", default)
        return self._record_call(
            "new_page", (url,), {"context_index": context_index}, returned
        )
