import logging
from typing import Generic

from ports.BrowserHandlers import HtmlElementActionInterface
from ports.BrowserHandlers.types import TBrowser, TElement, TPage


class PageHandlerInterface(Generic[TBrowser, TPage, TElement]):
    def __init__(
        self, page: TPage, action: HtmlElementActionInterface[TPage, TElement]
    ):
        self._page: TPage = page
        self.action = action
        self._logger = logging.getLogger(self.__class__.__name__)

    async def goto(self, url: str) -> None:
        raise NotImplementedError("PageHandlerInterface does not implement goto method")

    async def close(self) -> None:
        raise NotImplementedError("PageHandlerInterface does not implement close")

    async def html(self) -> str:
        raise NotImplementedError("PageHandlerInterface does not implement html")
