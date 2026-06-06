from typing import Generic

from ports.BrowserHandlers.types import TBrowser, TElement, TPage


class PageHandlerInterface(Generic[TBrowser, TPage, TElement]):
    async def goto(self, url: str) -> None:
        raise NotImplementedError("PageHandlerInterface does not implement goto method")

    async def close(self) -> None:
        raise NotImplementedError("PageHandlerInterface does not implement close")

    async def html(self) -> str:
        raise NotImplementedError("PageHandlerInterface does not implement html")

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
