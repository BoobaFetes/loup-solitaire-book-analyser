from typing import Callable

from playwright.async_api import Browser, async_playwright

from adapters.BrowserHandlers.types import (
    TBrowser,
    TElement,
    TPage,
)
from ports import BrowserInterface
from ports.BrowserHandlers import PageHandlerInterface


class BrowserAdapter(BrowserInterface[TBrowser, TPage, TElement]):
    def __init__(
        self,
        page_factory: Callable[
            [TPage], PageHandlerInterface[TBrowser, TPage, TElement]
        ],
    ):
        super().__init__()
        self._page_factory = page_factory
        self.browser: Browser = None  # type: ignore

    async def __aenter__(self):
        self.__context_manager = async_playwright()
        self.__playwright = await self.__context_manager.start()
        self.browser = await self.__playwright.chromium.launch(headless=True)
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

    async def new_page(
        self, url: str
    ) -> PageHandlerInterface[TBrowser, TPage, TElement]:
        page = await self.browser.new_page()
        page_handler = self._page_factory(page)
        await page_handler.goto(url)

        self.pages.append(page_handler)
        return page_handler

    async def close_page(self, index: int) -> bool:
        if index not in range(len(self.pages)):
            return False

        # the page will remove itself from the browser pages list when closed
        await self.pages[index].close()
        return True
