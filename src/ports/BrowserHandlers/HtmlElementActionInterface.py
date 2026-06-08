import logging
from typing import Generic, Literal

from ports.BrowserHandlers.types import TElement, TPage


class HtmlElementActionInterface(Generic[TPage, TElement]):
    def __init__(self, page: TPage):
        self._page: TPage = page
        self._logger = logging.getLogger(self.__class__.__name__)

    async def querySelector(self, css: str) -> TElement:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement querySelector"
        )

    async def querySelectorAll(self, css: str) -> list[TElement]:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement querySelectorAll"
        )

    async def get_by_text(self, text: str) -> TElement:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement get_by_text"
        )

    async def wait_element(
        self,
        element: TElement,
        *,
        timeout: float | None = 1.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
    ) -> bool:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement wait_element"
        )

    async def wait_for(
        self,
        selector: str,
        *,
        timeout: float | None = 1.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
    ) -> bool:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement wait_for"
        )

    async def wait_for_many(
        self,
        selectors: list[str],
        *,
        timeout: float | None = 1.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
    ) -> bool:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement wait_for_many"
        )

    async def get_value(
        self,
        css: str,
        value: str | None = None,
        *,
        timeout: float | None = 1.0,
    ) -> str:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement get_value"
        )

    async def set_value(self, css: str, value: bool | str) -> bool | str | None:
        raise NotImplementedError(
            "HtmlElementActionInterface does not implement set_value"
        )

    async def click(self, css: str) -> bool:
        raise NotImplementedError("HtmlElementActionInterface does not implement click")
