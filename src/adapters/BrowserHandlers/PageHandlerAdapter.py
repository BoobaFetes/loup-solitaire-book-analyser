import logging

from adapters.BrowserHandlers.types import TBrowser, TElement, TPage
from ports.BrowserHandlers.PageHandlerInterface import (
    PageHandlerInterface,
)


class PageHandlerAdapter(PageHandlerInterface[TBrowser, TPage, TElement]):
    def __init__(self, page: TPage):
        self._page: TPage = page
        self._logger = logging.getLogger(self.__class__.__name__)

    async def goto(self, url: str) -> None:
        await self._page.goto(url)

    async def close(self) -> None:
        await self._page.close()

    async def html(self) -> str:
        return await self._page.content()

    def querySelector(self, css: str) -> TElement | None:
        raise NotImplementedError(
            "PageHandlerInterface does not implement querySelector"
        )

    def querySelectorAll(self, css: str) -> list[TElement]:
        raise NotImplementedError(
            "PageHandlerInterface does not implement querySelectorAll"
        )

    async def wait_element(
        self, css: str, sleep: float = 0.5, timeout: float = 2.0
    ) -> TElement:
        raise NotImplementedError(
            "PageHandlerInterface does not implement wait_element"
        )
