from domain import Book
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeBookPriceUseCases(SpyStubFake):
    def __init__(self, books: list[Book]) -> None:
        super().__init__()
        self.books = books
        self.fetched_books: list[Book] = []

    def stub_fetch_prices(self, returned) -> None:
        self._stub("fetch_prices", returned)

    @property
    def spy_fetch_prices(self) -> list[SpyCall]:
        return self._spy("fetch_prices")

    def stub_bind_prices_to_books(self, returned: list[Book]) -> None:
        self._stub("bind_prices_to_books", returned)

    @property
    def spy_bind_prices_to_books(self) -> list[SpyCall]:
        return self._spy("bind_prices_to_books")

    async def fetch_prices(self, books: list[Book]):
        self.fetched_books = books
        default = {book.isbn: book.prices for book in books}
        returned = self._returned_or_default("fetch_prices", default)
        return self._record_call("fetch_prices", (books,), {}, returned)

    async def bind_prices_to_books(self, books: list[Book]) -> list[Book]:
        returned = self._returned_or_default("bind_prices_to_books", books)
        return self._record_call("bind_prices_to_books", (books,), {}, returned)
