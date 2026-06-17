import asyncio
from typing import cast

from playwright.async_api import Browser
from typing_extensions import Literal

from adapters.browser.BrowserAdapter import BrowserAdapter
from adapters.browser.types import TBrowser, TElement, TPage
from ports.browser import PageHandlerInterface


class FakePageHandler(PageHandlerInterface[TBrowser, TPage, TElement]):
    def __init__(self, page: TPage):
        self._page = page
        self.visited_urls: list[str] = []

    async def goto(
        self,
        url: str,
        *,
        wait_until: Literal["commit", "load", "domcontentloaded"] = "domcontentloaded",
        timeout: int = 10000,
    ) -> None:
        self.visited_urls.append(url)


class FakeContext:
    def __init__(self):
        self.pages: list[str] = []

    async def new_page(self):
        page = f"page-{len(self.pages)}"
        self.pages.append(page)
        return page


class FakeBrowser:
    def __init__(self):
        self.contexts = [FakeContext()]
        self.new_context_options: list[dict[str, object]] = []

    async def new_context(self, **kwargs):
        self.new_context_options.append(kwargs)
        self.contexts.append(FakeContext())


def test_new_context_uses_configured_browser_context_options():
    browser = BrowserAdapter(
        page_factory=FakePageHandler,
        browser_context_options={"locale": "fr-FR"},
        headless=True,
    )
    fake_browser = FakeBrowser()
    browser.browser = cast(Browser, fake_browser)

    context_index = asyncio.run(browser.new_context())

    assert context_index == 1
    assert fake_browser.new_context_options == [{"locale": "fr-FR"}]


def test_new_page_creates_handler_navigates_and_tracks_page():
    browser = BrowserAdapter(page_factory=FakePageHandler)
    browser.browser = cast(Browser, FakeBrowser())

    page_handler = asyncio.run(browser.new_page("https://example.test/livre"))

    assert isinstance(page_handler, FakePageHandler)
    assert page_handler._page == "page-0"
    assert page_handler.visited_urls == ["https://example.test/livre"]
    assert browser.pages == [page_handler]
