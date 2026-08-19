from domain import Book
from tests.fake.SpyStubFake import SpyCall, SpyStubFake
from usecases.book import OfficialBookUseCases


class FakeOfficialBookUseCases(OfficialBookUseCases, SpyStubFake):
    def __init__(self, books: list[Book]) -> None:
        SpyStubFake.__init__(self)
        self.books = books

    def stub_fetch_books(self, returned: list[Book]) -> None:
        self._stub("fetch_books", returned)

    @property
    def spy_fetch_books(self) -> list[SpyCall]:
        return self._spy("fetch_books")

    async def fetch_books(self, client=None) -> list[Book]:
        returned = self._returned_or_default("fetch_books", list(self.books))
        return self._record_call("fetch_books", (), {"client": client}, returned)
