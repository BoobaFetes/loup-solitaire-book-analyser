from collections.abc import Callable

from adapters.browser.tests.fake.FakeElement import FakeElement
from adapters.browser.tests.fake.FakeLocator import FakeLocator
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeBrowserPage(SpyStubFake):
    def __init__(self, element: FakeElement | None = None) -> None:
        super().__init__()
        self.element = element or FakeElement()
        self.url = "about:blank"
        self.goto_calls: list[tuple[str, str, int]] = []
        self.closed = False

    def stub_locator(self, returned: FakeLocator) -> None:
        self._stub("locator", returned)

    @property
    def spy_locator(self) -> list[SpyCall]:
        return self._spy("locator")

    def stub_get_by_role(self, returned: FakeElement) -> None:
        self._stub("get_by_role", returned)

    @property
    def spy_get_by_role(self) -> list[SpyCall]:
        return self._spy("get_by_role")

    def stub_goto(self, returned: None = None) -> None:
        self._stub("goto", returned)

    @property
    def spy_goto(self) -> list[SpyCall]:
        return self._spy("goto")

    def stub_wait_for_url(self, returned: None = None) -> None:
        self._stub("wait_for_url", returned)

    def stub_wait_for_url_exception(self, exception: BaseException) -> None:
        self._stub_exception("wait_for_url", exception)

    @property
    def spy_wait_for_url(self) -> list[SpyCall]:
        return self._spy("wait_for_url")

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

    def stub_content(self, returned: str) -> None:
        self._stub("content", returned)

    @property
    def spy_content(self) -> list[SpyCall]:
        return self._spy("content")

    def locator(self, css: str, **kwargs) -> FakeLocator:
        returned = self._returned_or_default("locator", FakeLocator([self.element]))
        return self._record_call("locator", (css,), kwargs, returned)

    def get_by_role(self, role: str, name: str) -> FakeElement:
        returned = self._returned_or_default("get_by_role", self.element)
        return self._record_call("get_by_role", (role, name), {}, returned)

    async def goto(self, url: str, *, wait_until: str, timeout: int) -> None:
        self.goto_calls.append((url, wait_until, timeout))
        self.url = url
        returned = self._returned_or_default("goto", None)
        return self._record_call(
            "goto", (url,), {"wait_until": wait_until, "timeout": timeout}, returned
        )

    async def wait_for_url(
        self,
        predicate: Callable[[str], bool],
        *,
        wait_until: str,
        timeout: int,
    ) -> None:
        self._raise_if_stubbed_exception("wait_for_url")
        self.wait_call = (wait_until, timeout)
        self.url = "https://example.test/changed"
        assert predicate(self.url)
        returned = self._returned_or_default("wait_for_url", None)
        return self._record_call(
            "wait_for_url",
            (predicate,),
            {"wait_until": wait_until, "timeout": timeout},
            returned,
        )

    async def title(self) -> str:
        returned = self._returned_or_default("title", "Titre")
        return self._record_call("title", (), {}, returned)

    async def close(self) -> None:
        self.closed = True
        returned = self._returned_or_default("close", None)
        return self._record_call("close", (), {}, returned)

    async def content(self) -> str:
        returned = self._returned_or_default("content", "<html></html>")
        return self._record_call("content", (), {}, returned)
