import logging
from typing import Generic

from ports.BrowserHandlers import (
    PageHandlerInterface,
    TBrowser,
    TElement,
    TPage,
)


class BrowserInterface(Generic[TBrowser, TPage, TElement]):
    def __init__(
        self,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)

        # protected instance attibutes

        # public instance attributes
        self.pages: list[PageHandlerInterface[TBrowser, TPage, TElement]] = []

    async def __aenter__(self) -> "BrowserInterface[TBrowser, TPage, TElement]":
        raise NotImplementedError("BrowserInterface does not implement __aenter__")

    async def __aexit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("BrowserInterface does not implement __aexit__")

    async def start(self) -> None:
        raise NotImplementedError("BrowserInterface does not implement start")

    async def new_page(
        self,
        url: str,
    ) -> PageHandlerInterface[TBrowser, TPage, TElement]:
        raise NotImplementedError("BrowserInterface does not implement new_page")

    async def close_page(self, index: int) -> bool:
        raise NotImplementedError("BrowserInterface does not implement close_page")
