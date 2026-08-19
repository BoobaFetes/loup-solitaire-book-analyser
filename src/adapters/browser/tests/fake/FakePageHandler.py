from typing import Literal, cast

from adapters.browser.types import TBrowser, TElement, TPage
from adapters.browser.tests.fake.FakeHtmlElementAction import FakeHtmlElementAction
from ports.browser import PageHandlerInterface
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakePageHandler(PageHandlerInterface[TBrowser, TPage, TElement], SpyStubFake):
    def __init__(
        self,
        page: TPage | None = None,
        *,
        html: str = "",
        matching_title: str = "",
        base_url: str = "https://www.amazon.fr",
    ) -> None:
        SpyStubFake.__init__(self)
        self._page = cast(TPage, page or object())
        self.action = FakeHtmlElementAction(object(), matching_title)
        self.visited_urls: list[str] = []
        self._html = html
        self.closed = False
        self._base_url = base_url
        self._current_url = base_url

    def stub_goto(self, returned: None = None) -> None:
        self._stub("goto", returned)

    @property
    def spy_goto(self) -> list[SpyCall]:
        return self._spy("goto")

    def stub_wait_for_url_change(self, returned: bool) -> None:
        self._stub("wait_for_url_change", returned)

    @property
    def spy_wait_for_url_change(self) -> list[SpyCall]:
        return self._spy("wait_for_url_change")

    def stub_current_url(self, returned: str) -> None:
        self._stub("current_url", returned)

    @property
    def spy_current_url(self) -> list[SpyCall]:
        return self._spy("current_url")

    def stub_title(self, returned: str) -> None:
        self._stub("title", returned)

    @property
    def spy_title(self) -> list[SpyCall]:
        return self._spy("title")

    def stub_close(self, returned: None = None) -> None:
        self._stub("close", returned)

    @property
    def spy_close(self) -> list[SpyCall]:
        return self._spy("close")

    def stub_html(self, returned: str) -> None:
        self._stub("html", returned)

    @property
    def spy_html(self) -> list[SpyCall]:
        return self._spy("html")

    async def goto(
        self,
        url: str,
        *,
        wait_until: Literal["commit", "load", "domcontentloaded"] = "domcontentloaded",
        timeout: int = 10000,
    ) -> None:
        self.visited_urls.append(url)
        self._current_url = url
        returned = self._returned_or_default("goto", None)
        return self._record_call(
            "goto", (url,), {"wait_until": wait_until, "timeout": timeout}, returned
        )

    async def wait_for_url_change(
        self, previous_url: str, timeout: int = 10000
    ) -> bool:
        self._current_url = f"{self._base_url}/s?k=fake"
        returned = self._returned_or_default("wait_for_url_change", True)
        return self._record_call(
            "wait_for_url_change", (previous_url,), {"timeout": timeout}, returned
        )

    async def current_url(self) -> str:
        returned = self._returned_or_default("current_url", self._current_url)
        return self._record_call("current_url", (), {}, returned)

    async def title(self) -> str:
        returned = self._returned_or_default("title", self.action.matching_title)
        return self._record_call("title", (), {}, returned)

    async def close(self) -> None:
        self.closed = True
        returned = self._returned_or_default("close", None)
        return self._record_call("close", (), {}, returned)

    async def html(self) -> str:
        returned = self._returned_or_default("html", self._html)
        return self._record_call("html", (), {}, returned)
