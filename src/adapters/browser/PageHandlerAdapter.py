from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from typing_extensions import Literal

from adapters.browser.HtmlElementActionAdapter import HtmlElementActionAdapter
from adapters.browser.types import TBrowser, TElement, TPage
from ports import PageHandlerInterface


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
        self._logger.info("Page loaded: %s", self._page.url)

    async def wait_for_url_change(
        self, previous_url: str, timeout: int = 10000
    ) -> bool:
        try:
            await self._page.wait_for_url(
                lambda url: str(url) != previous_url,
                wait_until="domcontentloaded",
                timeout=timeout,
            )
            self._logger.info("Page URL changed: %s", self._page.url)
            return True
        except PlaywrightTimeoutError:
            self._logger.warning(
                "Page URL did not change within %sms. Current URL: %s",
                timeout,
                self._page.url,
            )
            return False

    async def current_url(self) -> str:
        return self._page.url

    async def title(self) -> str:
        return await self._page.title()

    async def close(self) -> None:
        await self._page.close()

    async def html(self) -> str:
        return await self._page.content()
