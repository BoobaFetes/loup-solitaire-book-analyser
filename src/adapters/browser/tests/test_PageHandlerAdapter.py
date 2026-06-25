import asyncio
from typing import cast

from playwright.async_api import Page

from adapters.browser.PageHandlerAdapter import PageHandlerAdapter
from adapters.browser.tests.fake import FakeBrowserPage, TimeoutBrowserPage


def test_goto_delegates_to_page_with_defaults():
    page = FakeBrowserPage()
    handler = PageHandlerAdapter(cast(Page, page))

    asyncio.run(handler.goto("https://example.test"))

    assert page.goto_calls == [("https://example.test", "domcontentloaded", 10000)]


def test_wait_for_url_change_returns_true_when_url_changes():
    handler = PageHandlerAdapter(cast(Page, FakeBrowserPage()))

    assert asyncio.run(handler.wait_for_url_change("about:blank")) is True


def test_wait_for_url_change_returns_false_on_timeout():
    handler = PageHandlerAdapter(cast(Page, TimeoutBrowserPage()))

    assert asyncio.run(handler.wait_for_url_change("about:blank")) is False


def test_page_accessors_delegate_to_page():
    page = FakeBrowserPage()
    page.url = "https://example.test"
    handler = PageHandlerAdapter(cast(Page, page))

    assert asyncio.run(handler.current_url()) == "https://example.test"
    assert asyncio.run(handler.title()) == "Titre"
    assert asyncio.run(handler.html()) == "<html></html>"
    asyncio.run(handler.close())
    assert page.closed is True
