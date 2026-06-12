from typing_extensions import Literal

from adapters.BrowserHandlers.HtmlElementActionAdapter import HtmlElementActionAdapter
from adapters.BrowserHandlers.types import TBrowser, TElement, TPage
from ports.BrowserHandlers.PageHandlerInterface import (
    PageHandlerInterface,
)


class PageHandlerAdapter(PageHandlerInterface[TBrowser, TPage, TElement]):
    def __init__(self, page: TPage):
        super().__init__(page, HtmlElementActionAdapter(page))

    async def goto(
        self,
        url: str,
        *,
        wait_until: Literal["commit", "load", "domcontentloaded"] = "domcontentloaded",
        timeout: int = 10000,
    ) -> None:
        await self._page.goto(url, wait_until=wait_until, timeout=timeout)

    async def close(self) -> None:
        await self._page.close()

    async def html(self) -> str:
        return await self._page.content()
