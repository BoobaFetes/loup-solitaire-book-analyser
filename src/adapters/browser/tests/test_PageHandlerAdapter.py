import asyncio
from typing import cast

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from adapters.browser.PageHandlerAdapter import PageHandlerAdapter


class FakePage:
    def __init__(self):
        self.url = "about:blank"
        self.goto_calls = []
        self.closed = False

    async def goto(self, url: str, *, wait_until: str, timeout: int):
        self.goto_calls.append((url, wait_until, timeout))
        self.url = url

    async def wait_for_url(self, predicate, *, wait_until: str, timeout: int):
        self.wait_call = (wait_until, timeout)
        self.url = "https://example.test/changed"
        assert predicate(self.url)

    async def title(self):
        return "Titre"

    async def close(self):
        self.closed = True

    async def content(self):
        return "<html></html>"


class TimeoutPage(FakePage):
    async def wait_for_url(self, predicate, *, wait_until: str, timeout: int):
        raise PlaywrightTimeoutError("timeout")


def test_goto_delegates_to_page_with_defaults():
    page = FakePage()
    handler = PageHandlerAdapter(cast(Page, page))

    asyncio.run(handler.goto("https://example.test"))

    assert page.goto_calls == [("https://example.test", "domcontentloaded", 10000)]


def test_wait_for_url_change_returns_true_when_url_changes():
    handler = PageHandlerAdapter(cast(Page, FakePage()))

    assert asyncio.run(handler.wait_for_url_change("about:blank")) is True


def test_wait_for_url_change_returns_false_on_timeout():
    handler = PageHandlerAdapter(cast(Page, TimeoutPage()))

    assert asyncio.run(handler.wait_for_url_change("about:blank")) is False


def test_page_accessors_delegate_to_page():
    page = FakePage()
    page.url = "https://example.test"
    handler = PageHandlerAdapter(cast(Page, page))

    assert asyncio.run(handler.current_url()) == "https://example.test"
    assert asyncio.run(handler.title()) == "Titre"
    assert asyncio.run(handler.html()) == "<html></html>"
    asyncio.run(handler.close())
    assert page.closed is True
