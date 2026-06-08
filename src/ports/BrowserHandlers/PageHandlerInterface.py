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
        """Navigate to a specific URL.

        Args:
            url (str): The URL to navigate to.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("PageHandlerInterface does not implement goto method")

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
