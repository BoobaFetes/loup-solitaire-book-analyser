from typing import Literal, cast

from adapters.browser.types import TBrowser, TElement, TPage
from ports.browser import HtmlElementActionInterface, PageHandlerInterface


class FakeHtmlElementAction(HtmlElementActionInterface[object, object]):
    def __init__(self, page: object, matching_title: str = "") -> None:
        super().__init__(page)
        self.matching_title = matching_title
        self.values: dict[str, bool | str] = {}
        self.clicks: list[str] = []

    async def querySelector(self, css: str) -> object:
        return object()

    async def querySelectorAll(self, css: str) -> list[object]:
        return []

    async def wait_for(
        self,
        selector: str,
        *,
        retry: int = 3,
        timeout: float | None = 5.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
        **kwargs,
    ) -> bool:
        has_text = kwargs.get("has_text")
        if has_text is None:
            return True
        return bool(has_text.search(self.matching_title))

    async def get_value(self, css: str) -> str:
        value = self.values.get(css, "")
        return str(value)

    async def set_value(self, css: str, value: bool | str) -> bool | str | None:
        self.values[css] = value
        return value

    async def click(self, css: str) -> bool:
        self.clicks.append(css)
        return True


class FakePageHandler(PageHandlerInterface[TBrowser, TPage, TElement]):
    def __init__(
        self,
        page: TPage | None = None,
        *,
        html: str = "",
        matching_title: str = "",
        base_url: str = "https://www.amazon.fr",
    ) -> None:
        self._page = cast(TPage, page or object())
        self.action = FakeHtmlElementAction(object(), matching_title)
        self.visited_urls: list[str] = []
        self._html = html
        self.closed = False
        self._base_url = base_url
        self._current_url = base_url

    async def goto(
        self,
        url: str,
        *,
        wait_until: Literal["commit", "load", "domcontentloaded"] = "domcontentloaded",
        timeout: int = 10000,
    ) -> None:
        self.visited_urls.append(url)
        self._current_url = url

    async def wait_for_url_change(
        self, previous_url: str, timeout: int = 10000
    ) -> bool:
        self._current_url = f"{self._base_url}/s?k=fake"
        return True

    async def current_url(self) -> str:
        return self._current_url

    async def title(self) -> str:
        return self.action.matching_title

    async def close(self) -> None:
        self.closed = True

    async def html(self) -> str:
        return self._html
