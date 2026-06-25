from collections.abc import Callable

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from adapters.browser.tests.fake.FakeElement import FakeElement, FakeLocator


class FakeBrowserPage:
    def __init__(self, element: FakeElement | None = None) -> None:
        self.element = element or FakeElement()
        self.url = "about:blank"
        self.goto_calls: list[tuple[str, str, int]] = []
        self.closed = False

    def locator(self, css: str, **kwargs) -> FakeLocator:
        return FakeLocator([self.element])

    def get_by_role(self, role: str, name: str) -> FakeElement:
        return self.element

    async def goto(self, url: str, *, wait_until: str, timeout: int) -> None:
        self.goto_calls.append((url, wait_until, timeout))
        self.url = url

    async def wait_for_url(
        self,
        predicate: Callable[[str], bool],
        *,
        wait_until: str,
        timeout: int,
    ) -> None:
        self.wait_call = (wait_until, timeout)
        self.url = "https://example.test/changed"
        assert predicate(self.url)

    async def title(self) -> str:
        return "Titre"

    async def close(self) -> None:
        self.closed = True

    async def content(self) -> str:
        return "<html></html>"


class TimeoutBrowserPage(FakeBrowserPage):
    async def wait_for_url(
        self,
        predicate: Callable[[str], bool],
        *,
        wait_until: str,
        timeout: int,
    ) -> None:
        raise PlaywrightTimeoutError("timeout")
