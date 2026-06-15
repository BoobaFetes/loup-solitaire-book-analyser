import asyncio
from typing import cast

from adapters.browser.BrowserAdapter import BrowserAdapter
from adapters.browser.types import TBrowser, TElement, TPage
from ports.BrowserHandlers.PageHandlerInterface import PageHandlerInterface


class FakeBrowser:
    def __init__(self):
        self.contexts = []

    async def new_context(self, **kwargs):
        self.contexts.append(kwargs)


def test_new_context_uses_configured_browser_context_options():
    browser = BrowserAdapter(
        page_factory=lambda page: cast(
            PageHandlerInterface[TBrowser, TPage, TElement], page
        ),
        browser_context_options={
            "user_agent": "Mozilla/5.0 test",
            "viewport": {
                "width": 1920,
                "height": 1080,
            },
            "locale": "fr-FR",
            "timezone_id": "Europe/Paris",
            "extra_http_headers": {
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
            "java_script_enabled": True,
        },
        headless=True,
    )
    browser.browser = FakeBrowser()  # type: ignore[assignment]

    context_index = asyncio.run(browser.new_context())

    assert context_index == 0
    assert browser.browser.contexts == [
        {
            "user_agent": "Mozilla/5.0 test",
            "viewport": {
                "width": 1920,
                "height": 1080,
            },
            "locale": "fr-FR",
            "timezone_id": "Europe/Paris",
            "extra_http_headers": {
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
            "java_script_enabled": True,
        }
    ]
