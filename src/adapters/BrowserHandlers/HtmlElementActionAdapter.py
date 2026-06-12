from collections.abc import Awaitable, Callable
from logging import Logger
from typing import Generic, Literal, TypeVar

from adapters.BrowserHandlers.types import TElement, TPage
from ports.BrowserHandlers import HtmlElementActionInterface


class HtmlFileBackup:
    __html_file_counter: int = 0

    def __init__(self, logger):
        import os
        from pathlib import Path

        self._logger = logger
        self.directory = Path(os.getcwd()) / "logs/html"
        self.directory.mkdir(exist_ok=True)

    async def save(
        self,
        *,
        filename_pattern: Callable[[int], str],
        log_message: Callable[[str], str | None],
        html: str,
    ) -> None:
        HtmlFileBackup.__html_file_counter += 1
        filename = filename_pattern(HtmlFileBackup.__html_file_counter)

        path = f"./logs/html/{filename}.html"
        msg = log_message(path)
        if msg:
            self._logger.info(msg)

        file = self.directory / f"{filename}.html"
        with file.open("w", encoding="utf-8") as f:
            f.write(html)


TExecuteResult = TypeVar("TExecuteResult")


class RetryAction(Generic[TExecuteResult]):
    def __init__(self, logger: Logger):
        self.__logger = logger

    async def execute(
        self,
        action: Callable[[], Awaitable[TExecuteResult]],
        on_failure: Callable[[Exception], Awaitable[TExecuteResult]],
        retry_message: Callable[[int], str] | None = None,
        use_error_log: bool = True,
        retry: int = 3,
    ) -> TExecuteResult:
        if not retry_message:
            retry_message = lambda r: f"Action failed. Retrying... ({r} retries left)"  # noqa: E731

        try:
            return await action()
        except Exception as e:
            if retry > 0:
                self.__logger.warning(retry_message(retry))
                return await self.execute(
                    action,
                    on_failure=on_failure,
                    retry_message=retry_message,
                    use_error_log=use_error_log,
                    retry=retry - 1,
                )

            if use_error_log:
                self.__logger.error(f"Action failed after retries: {e}", exc_info=True)

            return await on_failure(e)


class HtmlElementActionAdapter(HtmlElementActionInterface[TPage, TElement]):
    def __init__(self, page: TPage, html_file_backup: HtmlFileBackup | None = None):
        super().__init__(page)
        self.__html_file_backup = (
            html_file_backup
            if html_file_backup is not None
            else HtmlFileBackup(self._logger)
        )
        self._retry_action = RetryAction(self._logger)

    @staticmethod
    def __selector_description(selector: str, state: str | None, kwargs: dict) -> str:
        details = f"selector '{selector}' in state '{state}'"
        if kwargs:
            details += f" with options {kwargs!r}"
        return details

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

        async def action_fn() -> bool:
            element = self._page.locator(selector, **kwargs).first
            await element.wait_for(
                state=state,
                timeout=None if timeout is None else int(timeout * 1000),
            )
            return True

        async def on_failure_fn(e: Exception) -> bool:
            selector_description = self.__selector_description(selector, state, kwargs)
            self._logger.error(
                f"Error while waiting for {selector_description}: {e}",
                exc_info=True,
            )
            await self.__html_file_backup.save(
                html=await self._page.content(),
                filename_pattern=lambda counter: f"wait_for_{counter}",
                log_message=lambda path: (
                    f"saving page for {selector_description} in '{path}'"
                ),
            )
            return False

        retry_action = RetryAction[bool](self._logger)
        return await retry_action.execute(
            action=action_fn,
            on_failure=on_failure_fn,
            retry_message=lambda r: (
                f"Element with {self.__selector_description(selector, state, kwargs)} "
                f"not found. Retrying... ({r} retries left)"
            ),
            use_error_log=False,
            retry=retry,
        )

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
