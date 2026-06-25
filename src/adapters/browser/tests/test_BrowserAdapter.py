import asyncio
from typing import cast

from playwright.async_api import Browser

from adapters.browser.BrowserAdapter import BrowserAdapter
from adapters.browser.tests.fake import FakeBrowser, FakePageHandler


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
    fake_browser = FakeBrowser()
    browser.browser = cast(Browser, fake_browser)

    page_handler = asyncio.run(browser.new_page("https://example.test/livre"))

    assert isinstance(page_handler, FakePageHandler)
    assert page_handler._page is fake_browser.contexts[0].pages[0]
    assert page_handler.visited_urls == ["https://example.test/livre"]
    assert browser.pages == [page_handler]
