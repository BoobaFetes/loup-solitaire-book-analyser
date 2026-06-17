import logging
from typing import Generic, Literal

from ports.browser.HtmlElementActionInterface import HtmlElementActionInterface
from ports.browser.types import TBrowser, TElement, TPage


class PageHandlerInterface(Generic[TBrowser, TPage, TElement]):
    def __init__(
        self, page: TPage, action: HtmlElementActionInterface[TPage, TElement]
    ):
        self._page: TPage = page
        self.action = action
        self._logger = logging.getLogger(self.__class__.__name__)

    async def goto(
        self,
        url: str,
        *,
        wait_until: Literal["commit", "load", "domcontentloaded"] = "domcontentloaded",
        timeout: int = 10000,
    ) -> None:
        """Navigate to a specific URL.

        Args:
            url (str): The URL to navigate to.
            wait_until (Literal["commit", "load", "domcontentloaded"]): When to consider navigation succeeded.
            timeout (int): The maximum time to wait for the page to load, in milliseconds. (default is 10 seconds - 10k ms)

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("PageHandlerInterface does not implement goto method")

    async def wait_for_url_change(
        self, previous_url: str, timeout: int = 10000
    ) -> bool:
        """Wait until the current page URL changes."""
        raise NotImplementedError(
            "PageHandlerInterface does not implement wait_for_url_change"
        )

    async def current_url(self) -> str:
        """Get the current page URL."""
        raise NotImplementedError("PageHandlerInterface does not implement current_url")

    async def title(self) -> str:
        """Get the current page title."""
        raise NotImplementedError("PageHandlerInterface does not implement title")

    async def close(self) -> None:
        """Close the page.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("PageHandlerInterface does not implement close")

    async def html(self) -> str:
        """Get the HTML content of the page.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            str: The HTML content of the page.
        """
        raise NotImplementedError("PageHandlerInterface does not implement html")
