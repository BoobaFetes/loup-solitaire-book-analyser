from adapters.browser.tests.fake.FakeElement import FakeElement
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeLocator(SpyStubFake):
    def __init__(self, elements: list[FakeElement]) -> None:
        super().__init__()
        self.elements = elements
        self.first = elements[0]

    def stub_all(self, returned: list[FakeElement]) -> None:
        self._stub("all", returned)

    @property
    def spy_all(self) -> list[SpyCall]:
        return self._spy("all")

    def stub_check(self, returned: None = None) -> None:
        self._stub("check", returned)

    @property
    def spy_check(self) -> list[SpyCall]:
        return self._spy("check")

    async def all(self) -> list[FakeElement]:
        returned = self._returned_or_default("all", self.elements)
        return self._record_call("all", (), {}, returned)

    async def check(self) -> None:
        await self.first.check()
        returned = self._returned_or_default("check", None)
        return self._record_call("check", (), {}, returned)
