import asyncio
import traceback
from typing import Literal

from adapters.BrowserHandlers.types import TElement, TPage
from ports.BrowserHandlers import HtmlElementActionInterface


class HtmlElementActionAdapter(HtmlElementActionInterface[TPage, TElement]):
    def __init__(self, page: TPage):
        super().__init__(page)

    async def querySelector(self, css: str) -> TElement:
        """Get the first element matching a CSS selector.
        Args:
            css (str): The CSS selector to match the element.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            TElement: The first element matching the CSS selector.
        """
        element = self._page.locator(css)
        return element.first

    async def querySelectorAll(self, css: str) -> list[TElement]:
        """Get all elements matching a CSS selector.

        Args:
            css (str): The CSS selector to match the elements.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            list[TElement]: A list of elements matching the CSS selector.
        """
        elements = self._page.locator(css)
        return await elements.all()

    async def get_by_text(self, text: str) -> TElement:
        """Get the first element matching the given text.

        Args:
            text (str): The text to match the element.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            TElement: The first element matching the text.
        """
        element = self._page.get_by_text(text)
        return element.first

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

        Returns:
            bool: True if the element reached the desired state within the timeout, False otherwise.
        """
        try:
            await element.wait_for(timeout=self.__convert_in_ms(timeout), state=state)
            return True
        except Exception as e:
            self._logger.error(
                f"Error while waiting for element {element}: {e}",
                exc_info=True,
            )
            return False

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

        Returns:
            bool: True if the element reached the desired state within the timeout, False otherwise.
        """
        element = self._page.locator(selector)
        if not element:
            self._logger.error(f"No element found for selector: {selector}")
            return False

        try:
            await element.wait_for(timeout=self.__convert_in_ms(timeout), state=state)
        except Exception as e:
            self._logger.error(
                f"Error while waiting for element {selector}: {e}",
                exc_info=True,
            )
            return False

        return True

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

        Returns:
            bool: True if all elements reached the desired state within the timeout, False otherwise.
        """
        valid_selectors = [s for s in selectors if s]
        if not valid_selectors:
            return False

        elements = [self._page.locator(selector) for selector in valid_selectors]
        exceptions = await asyncio.gather(
            *[
                element.wait_for(timeout=self.__convert_in_ms(timeout), state=state)
                for element in elements
            ],
            return_exceptions=True,
        )

        fails = any(e is not None for e in exceptions)
        if fails:
            msgs = ["Errors while waiting for elements: "]
            for i, exc in [(i, exc) for i, exc in enumerate(exceptions) if exc]:
                tb = "".join(
                    traceback.format_exception(type(exc), exc, exc.__traceback__)
                )
                msgs.append(f" {i}. {valid_selectors[i]} : {tb}")
            self._logger.error("\n".join(msgs))

        return not fails

    def __convert_in_ms(self, timeout: float | None) -> int | None:
        return None if timeout is None else int(timeout * 1000)

    async def get_value(
        self,
        css: str,
    ) -> str:
        """Get the value of an element matching a CSS selector, or set it if a value is provided.
        Args:
            css (str): The CSS selector to match the element.

        Returns:
            str: The value of the element.
        """
        element = await self.querySelector(css)
        if not element:
            self._logger.error(f"No element found for selector: {css}")
            return ""

        return await element.input_value()

    async def set_value(self, css: str, value: bool | str) -> bool | str | None:
        """Set the value of an element matching a CSS selector.

        Args:
            css (str): The CSS selector to match the element.
            value (bool | str): The value to set.

        Returns:
            bool | str | None: The result of the operation.
        """
        element = await self.querySelector(css)
        tag = await element.evaluate("el => el.tagName.toLowerCase()")
        type_attr = await element.evaluate("el => el.getAttribute('type')")
        role = await element.evaluate("el => el.getAttribute('role')")

        match (tag, type_attr, role):
            # --- TEXT INPUT / TEXTAREA ---
            case (
                "input" | "textarea",
                None | "text" | "search" | "email" | "password" | "number",
                _,
            ):
                await element.fill(str(value))

            # --- RADIO ---
            case ("input", "radio", _):
                radio = self._page.locator(f'{css}[value="{value}"]')
                await radio.check()

            # --- CHECKBOX ---
            case ("input", "checkbox", _):
                if bool(value):
                    await element.check()
                else:
                    await element.uncheck()

            # --- SELECT (HTML COMBOBOX) ---
            case ("select", _, _):
                await element.select_option(str(value))

            # --- ARIA COMBOBOX (Playwright) ---
            case (_, _, "combobox"):
                await element.click()
                option = self._page.get_by_role("option", name=str(value))
                await option.click()

            # --- FALLBACK ---
            case _:
                # last attempt: we try to use fill()
                try:
                    await element.fill(str(value))
                except Exception as e:
                    raise RuntimeError(
                        f"Unable to set value on {css} : element of type {tag} with type {type_attr} and role {role}"
                    ) from e

        result = await element.input_value()
        return result

    async def click(self, css: str) -> bool:
        """Click an element matching a CSS selector.

        Args:
            css (str): The CSS selector to match the element.

        Returns:
            bool: True if the element was clicked successfully, False otherwise.
        """
        element = await self.querySelector(css)
        if not element:
            self._logger.error(f"No element found for selector: {css}")
            return False

        try:
            await element.click()
            return True
        except Exception as e:
            self._logger.error(
                f"Error while clicking on element {css}: {e}",
                exc_info=True,
            )
            return False
