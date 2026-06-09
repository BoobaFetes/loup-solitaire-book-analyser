import logging
from typing import Generic, Literal

from ports.BrowserHandlers.types import TElement, TPage


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

    async def get_by_text(self, text: str) -> TElement:
        """Get an element by its text content.

        Args:
            text (str): The text content to search for.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            TElement: The element with the specified text content.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement get_by_text"
        )

    async def wait_element(
        self,
        element: TElement,
        *,
        timeout: float | None = 5.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
    ) -> bool:
        """Wait for an element to reach a specific state.

        Args:
            element (TElement): The element to wait for.
            timeout (float | None, optional): The maximum time to wait in seconds. Defaults to 5 seconds.
            state (Literal["attached", "detached", "hidden", "visible"] | None, optional): The state to wait for. Defaults to "attached".

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            bool: True if the element reached the desired state within the timeout, False otherwise.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement wait_element"
        )

    async def wait_for(
        self,
        selector: str,
        *,
        timeout: float | None = 5.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
    ) -> bool:
        """Wait for an element matching a CSS selector to reach a specific state.
        Args:
            selector (str): The CSS selector to match the element.
            timeout (float | None, optional): The maximum time to wait in seconds. Defaults to 5 seconds.
            state (Literal["attached", "detached", "hidden", "visible"] | None, optional): The state to wait for. Defaults to "attached".
        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        Returns:
            bool: True if the element reached the desired state within the timeout, False otherwise.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement wait_for"
        )

    async def wait_for_many(
        self,
        selectors: list[str],
        *,
        timeout: float | None = 5.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
    ) -> bool:
        """Wait for multiple elements matching CSS selectors to reach a specific state.

        Args:
            selectors (list[str]): The CSS selectors to match the elements.
            timeout (float | None, optional): The maximum time to wait in seconds. Defaults to 5 seconds.
            state (Literal["attached", "detached", "hidden", "visible"] | None, optional): The state to wait for. Defaults to "attached".

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            bool: True if all elements reached the desired state within the timeout, False otherwise.
        """
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement wait_for_many"
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
