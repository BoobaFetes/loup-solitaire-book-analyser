from typing import Literal

from adapters.browser.types import TBrowser, TElement, TPage
from ports.browser import PageHandlerInterface


class FakePageHandler(PageHandlerInterface[TBrowser, TPage, TElement]):
    def __init__(self, page: TPage) -> None:
        self._page = page
        self.visited_urls: list[str] = []

    async def goto(
        self,
        url: str,
        *,
        wait_until: Literal["commit", "load", "domcontentloaded"] = "domcontentloaded",
        timeout: int = 10000,
    ) -> None:
        self.visited_urls.append(url)

    async def wait_for_url_change(
        self, previous_url: str, timeout: int = 10000
    ) -> bool:
        return True

    async def current_url(self) -> str:
        return ""

    async def title(self) -> str:
        return ""

    async def close(self) -> None:
        pass

    async def html(self) -> str:
        return ""
