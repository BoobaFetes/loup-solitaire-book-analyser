import logging
from typing import Generic, Literal

from ports.browser.types import TElement, TPage


class HtmlElementActionInterface(Generic[TPage, TElement]):
    def __init__(self, page: TPage):
        self._page: TPage = page
        self._logger = logging.getLogger(self.__class__.__name__)

    async def querySelector(self, css: str) -> TElement:
        """Get the first element matching a CSS selector.

        Args:
            css (str): The CSS selector to match the element.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            TElement: The first element matching the CSS selector.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement querySelector"
        )

    async def querySelectorAll(self, css: str) -> list[TElement]:
        """Get all elements matching a CSS selector.

        Args:
            css (str): The CSS selector to match elements.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            list[TElement]: A list of elements matching the CSS selector.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement querySelectorAll"
        )

    async def wait_for(
        self,
        selector: str,
        *,
        retry: int = 3,
        timeout: float | None = 5.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
        **kwargs,
    ) -> bool:
        """Wait for an element matching a CSS selector to reach a specific state.
        Args:
            selector (str): The CSS selector to match the element.
            retry (int, optional): The number of times to retry the search. Defaults to 3.
            timeout (float | None, optional): The maximum time to wait in seconds. Defaults to 5 seconds.
            state (Literal["attached", "detached", "hidden", "visible"] | None, optional): The state to wait for. Defaults to "attached".
            **kwargs: Additional keyword arguments to pass to the underlying implementation.
        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        Returns:
            bool: True if the element reached the desired state within the timeout, False otherwise.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement wait_for"
        )

    async def get_value(
        self,
        css: str,
    ) -> str:
        """Get the value of an element matching a CSS selector.

        Args:
            css (str): The CSS selector to match the element.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            str: The value of the element.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement get_value"
        )

    async def set_value(self, css: str, value: bool | str) -> bool | str | None:
        """Set the value of an element matching a CSS selector.

        Args:
            css (str): The CSS selector to match the element.
            value (bool | str): The value to set.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            bool | str | None: The result of the operation.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement set_value"
        )

    async def click(self, css: str) -> bool:
        """Click an element matching a CSS selector.

        Args:
            css (str): The CSS selector to match the element.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            bool: True if the click was successful, False otherwise.
        """
        raise NotImplementedError("HtmlElementActionInterface does not implement click")
