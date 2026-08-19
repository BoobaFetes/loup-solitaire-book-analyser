from domain import Book, BookPrice
from tests.fake.SpyStubFake import SpyCall, SpyStubFake
from usecases.price.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class FakePriceSourceUsecases(PriceSourceUsecasesBase, SpyStubFake):
    def __init__(self, base_url: str, prices: list[BookPrice]) -> None:
        super().__init__(base_url)
        SpyStubFake.__init__(self)
        self.prices = prices
        self.requested_books: list[Book] = []

    def stub_fetch_bookprices(self, returned: list[BookPrice]) -> None:
        self._stub("fetch_bookprices", returned)

    @property
    def spy_fetch_bookprices(self) -> list[SpyCall]:
        return self._spy("fetch_bookprices")

    def stub_fetch_bookprice(self, returned: BookPrice | None) -> None:
        self._stub("fetch_bookprice", returned)

    @property
    def spy_fetch_bookprice(self) -> list[SpyCall]:
        return self._spy("fetch_bookprice")

    async def fetch_bookprices(self, books: list[Book]) -> list[BookPrice]:
        self.requested_books = list(books)
        returned = self._returned_or_default("fetch_bookprices", list(self.prices))
        return self._record_call("fetch_bookprices", (books,), {}, returned)

    async def fetch_bookprice(self, book: Book, **kwargs) -> BookPrice | None:
        default = next(
            (price for price in self.prices if price.isbn == book.isbn), None
        )
        returned = self._returned_or_default("fetch_bookprice", default)
        return self._record_call("fetch_bookprice", (book,), kwargs, returned)
