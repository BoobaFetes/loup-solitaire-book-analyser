from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeOfficialPriceDetailsFinder(SpyStubFake):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.html = html

    def stub_price_and_currency(self, returned: tuple[float, str]) -> None:
        self._stub("price_and_currency", returned)

    @property
    def spy_price_and_currency(self) -> list[SpyCall]:
        return self._spy("price_and_currency")

    def price_and_currency(self) -> tuple[float, str]:
        default = (0.0, "not set") if "no-price" in self.html else (12.345, "EUR")
        returned = self._returned_or_default("price_and_currency", default)
        return self._record_call("price_and_currency", (), {}, returned)
