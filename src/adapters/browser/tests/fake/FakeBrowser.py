from typing import cast

from adapters.browser.tests.fake.FakeBrowserPage import FakeBrowserPage
from adapters.browser.tests.fake.FakePageHandler import FakePageHandler
from ports.browser import BrowserInterface, PageHandlerInterface


class FakeBrowserContext:
    def __init__(self) -> None:
        self.pages: list[FakeBrowserPage] = []

    async def new_page(self) -> FakeBrowserPage:
        page = FakeBrowserPage()
        self.pages.append(page)
        return page


class FakeBrowser(BrowserInterface[object, object, object]):
    def __init__(self, page_handler: FakePageHandler | None = None) -> None:
        super().__init__()
        self.page_handler = page_handler
        self.contexts = [FakeBrowserContext()]
        self.new_context_options: list[dict[str, object]] = []
        self.opened = False

    async def __aenter__(self) -> "FakeBrowser":
        self.opened = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.opened = False

    async def start(self) -> None:
        self.opened = True

    async def close(self) -> None:
        self.opened = False

    async def new_context(self, **kwargs) -> int:
        self.new_context_options.append(kwargs)
        self.contexts.append(FakeBrowserContext())
        return len(self.contexts) - 1

    async def new_page(
        self, url: str, context_index: int = 0
    ) -> PageHandlerInterface[object, object, object]:
        if self.page_handler is None:
            self.page_handler = FakePageHandler(base_url=url)
        return cast(PageHandlerInterface[object, object, object], self.page_handler)
