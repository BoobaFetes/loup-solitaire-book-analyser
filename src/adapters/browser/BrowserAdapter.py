from typing import Any, Callable

from playwright.async_api import Browser, async_playwright

from adapters.browser.types import (
    TBrowser,
    TElement,
    TPage,
)
from ports import BrowserInterface, PageHandlerInterface


class BrowserAdapter(BrowserInterface[TBrowser, TPage, TElement]):
    def __init__(
        self,
        page_factory: Callable[
            [TPage], PageHandlerInterface[TBrowser, TPage, TElement]
        ],
        browser_context_options: dict[str, Any] | None = None,
        **kwargs,
    ):
        super().__init__()
        self._page_factory = page_factory
        self.browser: Browser = None  # type: ignore
        self.__options = kwargs
        self.__context_options = browser_context_options or {}

    async def __aenter__(self):
        self.__context_manager = async_playwright()
        self.__playwright = await self.__context_manager.start()
        self.browser = await self.__playwright.chromium.launch(**self.__options)
        self._logger.info("Browser launch options: %s", self.__options)
        self._logger.info("Browser context options: %s", self.__context_options)
        self.browser.on(
            "context", lambda browser: self._logger.info("Browser connected")
        )
        self.browser.on(
            "disconnected", lambda browser: self._logger.info("Browser disconnected")
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__context_manager.__aexit__(exc_type, exc_value, traceback)
        self.__playwright = None
        self.browser = None  # type: ignore

    async def start(self) -> None:
        await self.__aenter__()

    async def close(self) -> None:
        await self.__aexit__(None, None, None)

    async def new_context(self) -> int:
        index = len(self.browser.contexts)
        await self.browser.new_context(**self.__context_options)
        return index

    async def new_page(
        self,
        url: str,
        context_index: int = 0,
    ) -> PageHandlerInterface[TBrowser, TPage, TElement]:
        context = self.browser.contexts[context_index]
        page = await context.new_page()
        page_handler = self._page_factory(page)
        await page_handler.goto(url)

        self.pages.append(page_handler)
        return page_handler
