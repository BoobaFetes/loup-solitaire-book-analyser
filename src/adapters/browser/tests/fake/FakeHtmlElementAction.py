from typing import Literal

from ports.browser import HtmlElementActionInterface
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeHtmlElementAction(HtmlElementActionInterface[object, object], SpyStubFake):
    def __init__(self, page: object, matching_title: str = "") -> None:
        super().__init__(page)
        SpyStubFake.__init__(self)
        self.matching_title = matching_title
        self.values: dict[str, bool | str] = {}
        self.clicks: list[str] = []

    def stub_querySelector(self, returned: object) -> None:
        self._stub("querySelector", returned)

    @property
    def spy_querySelector(self) -> list[SpyCall]:
        return self._spy("querySelector")

    def stub_querySelectorAll(self, returned: list[object]) -> None:
        self._stub("querySelectorAll", returned)

    @property
    def spy_querySelectorAll(self) -> list[SpyCall]:
        return self._spy("querySelectorAll")

    def stub_wait_for(self, returned: bool) -> None:
        self._stub("wait_for", returned)

    @property
    def spy_wait_for(self) -> list[SpyCall]:
        return self._spy("wait_for")

    def stub_get_value(self, returned: str) -> None:
        self._stub("get_value", returned)

    @property
    def spy_get_value(self) -> list[SpyCall]:
        return self._spy("get_value")

    def stub_set_value(self, returned: bool | str | None) -> None:
        self._stub("set_value", returned)

    @property
    def spy_set_value(self) -> list[SpyCall]:
        return self._spy("set_value")

    def stub_click(self, returned: bool) -> None:
        self._stub("click", returned)

    @property
    def spy_click(self) -> list[SpyCall]:
        return self._spy("click")

    async def querySelector(self, css: str) -> object:
        returned = self._returned_or_default("querySelector", object())
        return self._record_call("querySelector", (css,), {}, returned)

    async def querySelectorAll(self, css: str) -> list[object]:
        returned = self._returned_or_default("querySelectorAll", [])
        return self._record_call("querySelectorAll", (css,), {}, returned)

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
            default = True
        else:
            default = bool(has_text.search(self.matching_title))
        returned = self._returned_or_default("wait_for", default)
        return self._record_call(
            "wait_for",
            (selector,),
            {
                "retry": retry,
                "timeout": timeout,
                "state": state,
                **kwargs,
            },
            returned,
        )

    async def get_value(self, css: str) -> str:
        value = self.values.get(css, "")
        returned = self._returned_or_default("get_value", str(value))
        return self._record_call("get_value", (css,), {}, returned)

    async def set_value(self, css: str, value: bool | str) -> bool | str | None:
        self.values[css] = value
        returned = self._returned_or_default("set_value", value)
        return self._record_call("set_value", (css, value), {}, returned)

    async def click(self, css: str) -> bool:
        self.clicks.append(css)
        returned = self._returned_or_default("click", True)
        return self._record_call("click", (css,), {}, returned)
