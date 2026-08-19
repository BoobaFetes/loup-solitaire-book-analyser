import asyncio
from typing import cast

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from adapters.browser.PageHandlerAdapter import PageHandlerAdapter
from adapters.browser.tests.fake import FakeBrowserPage


def test_goto_delegates_to_page_with_defaults():

    # Arrange
    page = FakeBrowserPage()
    handler = PageHandlerAdapter(cast(Page, page))

    # Act
    asyncio.run(handler.goto("https://example.test"))

    # Assert
    assert page.goto_calls == [("https://example.test", "domcontentloaded", 10000)]


def test_wait_for_url_change_returns_true_when_url_changes():

    # Arrange
    handler = PageHandlerAdapter(cast(Page, FakeBrowserPage()))

    # Act
    actual = asyncio.run(handler.wait_for_url_change("about:blank"))

    # Assert
    expected = True
    assert actual is expected


def test_wait_for_url_change_returns_false_on_timeout():

    # Arrange
    page = FakeBrowserPage()
    page.stub_wait_for_url_exception(PlaywrightTimeoutError("timeout"))
    handler = PageHandlerAdapter(cast(Page, page))

    # Act
    actual = asyncio.run(handler.wait_for_url_change("about:blank"))

    # Assert
    expected = False
    assert actual is expected


def test_page_accessors_delegate_to_page():

    # Arrange
    page = FakeBrowserPage()
    page.url = "https://example.test"
    handler = PageHandlerAdapter(cast(Page, page))

    # Act
    actual = asyncio.run(handler.current_url())

    # Assert
    expected = "https://example.test"
    assert actual == expected
    actual = asyncio.run(handler.title())

    expected = "Titre"
    assert actual == expected
    actual = asyncio.run(handler.html())

    expected = "<html></html>"
    assert actual == expected
    asyncio.run(handler.close())
    assert page.closed is True
