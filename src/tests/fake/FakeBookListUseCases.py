from domain import Book
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeBookListUseCases(SpyStubFake):
    def __init__(self, books: list[Book]) -> None:
        super().__init__()
        self.books = books

    def stub_fetch_books(self, returned: list[Book]) -> None:
        self._stub("fetch_books", returned)

    @property
    def spy_fetch_books(self) -> list[SpyCall]:
        return self._spy("fetch_books")

    def stub_list(self, returned: list[Book]) -> None:
        self._stub("list", returned)

    @property
    def spy_list(self) -> list[SpyCall]:
        return self._spy("list")

    async def fetch_books(self) -> list[Book]:
        returned = self._returned_or_default("fetch_books", self.books)
        return self._record_call("fetch_books", (), {}, returned)

    async def list(self) -> list[Book]:
        returned = self._returned_or_default("list", self.books)
        return self._record_call("list", (), {}, returned)
