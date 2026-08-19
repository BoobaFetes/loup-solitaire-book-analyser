from typing import Literal

from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeElement(SpyStubFake):
    def __init__(
        self,
        tag: str = "input",
        type_attr: str | None = "text",
        role: str | None = None,
        value: str = "",
    ) -> None:
        super().__init__()
        self.tag = tag
        self.type_attr = type_attr
        self.role = role
        self.value = value
        self.clicked = False
        self.checked = False
        self.wait_calls: list[
            tuple[Literal["attached", "detached", "hidden", "visible"] | None, int]
        ] = []

    def stub_evaluate(self, returned: str | None) -> None:
        self._stub("evaluate", returned)

    @property
    def spy_evaluate(self) -> list[SpyCall]:
        return self._spy("evaluate")

    def stub_fill(self, returned: None = None) -> None:
        self._stub("fill", returned)

    def stub_fill_exception(self, exception: BaseException) -> None:
        self._stub_exception("fill", exception)

    @property
    def spy_fill(self) -> list[SpyCall]:
        return self._spy("fill")

    def stub_input_value(self, returned: str) -> None:
        self._stub("input_value", returned)

    @property
    def spy_input_value(self) -> list[SpyCall]:
        return self._spy("input_value")

    def stub_click(self, returned: None = None) -> None:
        self._stub("click", returned)

    def stub_click_exception(self, exception: BaseException) -> None:
        self._stub_exception("click", exception)

    @property
    def spy_click(self) -> list[SpyCall]:
        return self._spy("click")

    def stub_check(self, returned: None = None) -> None:
        self._stub("check", returned)

    @property
    def spy_check(self) -> list[SpyCall]:
        return self._spy("check")

    def stub_uncheck(self, returned: None = None) -> None:
        self._stub("uncheck", returned)

    @property
    def spy_uncheck(self) -> list[SpyCall]:
        return self._spy("uncheck")

    def stub_select_option(self, returned: None = None) -> None:
        self._stub("select_option", returned)

    @property
    def spy_select_option(self) -> list[SpyCall]:
        return self._spy("select_option")

    def stub_wait_for(self, returned: None = None) -> None:
        self._stub("wait_for", returned)

    @property
    def spy_wait_for(self) -> list[SpyCall]:
        return self._spy("wait_for")

    async def evaluate(self, expression: str) -> str | None:
        if "tagName" in expression:
            default = self.tag
        elif "type" in expression:
            default = self.type_attr
        elif "role" in expression:
            default = self.role
        else:
            default = None
        returned = self._returned_or_default("evaluate", default)
        return self._record_call("evaluate", (expression,), {}, returned)

    async def fill(self, value: str) -> None:
        self._raise_if_stubbed_exception("fill")
        self.value = value
        returned = self._returned_or_default("fill", None)
        return self._record_call("fill", (value,), {}, returned)

    async def input_value(self) -> str:
        returned = self._returned_or_default("input_value", self.value)
        return self._record_call("input_value", (), {}, returned)

    async def click(self) -> None:
        self._raise_if_stubbed_exception("click")
        self.clicked = True
        returned = self._returned_or_default("click", None)
        return self._record_call("click", (), {}, returned)

    async def check(self) -> None:
        self.checked = True
        returned = self._returned_or_default("check", None)
        return self._record_call("check", (), {}, returned)

    async def uncheck(self) -> None:
        self.checked = False
        returned = self._returned_or_default("uncheck", None)
        return self._record_call("uncheck", (), {}, returned)

    async def select_option(self, value: str) -> None:
        self.value = value
        returned = self._returned_or_default("select_option", None)
        return self._record_call("select_option", (value,), {}, returned)

    async def wait_for(
        self,
        *,
        state: Literal["attached", "detached", "hidden", "visible"] | None,
        timeout: int,
    ) -> None:
        self.wait_calls.append((state, timeout))
        returned = self._returned_or_default("wait_for", None)
        return self._record_call(
            "wait_for", (), {"state": state, "timeout": timeout}, returned
        )
