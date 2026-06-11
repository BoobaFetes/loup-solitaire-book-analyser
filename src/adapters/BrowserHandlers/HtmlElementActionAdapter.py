from typing import Literal

from adapters.BrowserHandlers.types import TElement, TPage
from ports.BrowserHandlers import HtmlElementActionInterface


class HtmlElementActionAdapter(HtmlElementActionInterface[TPage, TElement]):
    def __init__(self, page: TPage):
        super().__init__(page)

    async def __save_page_in_html_file(
        self, filename: str, html: str | None = None
    ) -> None:
        import os
        from pathlib import Path

        directory = Path(os.getcwd()) / "logs/html"
        directory.mkdir(exist_ok=True)

        file = directory / f"{filename}.html"
        with file.open("w", encoding="utf-8") as f:
            f.write(html if html is not None else await self._page.content())

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

    
    html_file_counter=0
    async def wait_for(
        self,
        selector: str,
        *,
        retry: int = 3,
        timeout: float | None = 10.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "visible",
        **kwargs,
    ) -> bool:
        """Wait for an element matching a CSS selector to reach a specific state.

        Args:
            selector (str): The CSS selector to match the element.
            retry (int, optional): The number of times to retry the search. Defaults to 3.
            timeout (float | None, optional): The maximum time to wait in seconds. Defaults to 10 seconds.
            state (Literal["attached", "detached", "hidden", "visible"] | None, optional): The state to wait for. Defaults to "visible".
            **kwargs: Additional keyword arguments to pass to the underlying implementation.

        Returns:
            bool: True if the element reached the desired state within the timeout, False otherwise.
        """

        async def rety_fn(e: Exception) -> bool:
            if retry > 0:
                self._logger.warning(
                    f"Element with selector '{selector}' not found in state '{state}'. Retrying... ({retry} retries left)"
                )
                return await self.wait_for(
                    selector, retry=retry - 1, timeout=timeout, state=state
                )
            self._logger.error(
                f"Error while waiting for selector {selector}: {e}",
                exc_info=True,
            )
            
            HtmlElementActionAdapter.html_file_counter += 1
            file_selector = f"wait_for_{HtmlElementActionAdapter.html_file_counter}"
            self._logger.info(f"saving page for selector '{selector}' in './logs/html/{file_selector}.html'")
            await self.__save_page_in_html_file(file_selector)
            return False

        element = self._page.locator(selector, **kwargs).first
        if not element:
            self._logger.error(f"No element found for selector: {selector}")
            return False

        try:
            await element.wait_for(timeout=self.__convert_in_ms(timeout), state=state)
        except Exception as e:
            return await rety_fn(e)

        return True

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
