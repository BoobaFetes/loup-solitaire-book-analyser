from domain import Book
from usecases.book import NonOfficialBookUseCases, OfficialBookUseCases


class FakeOfficialBookUseCases(OfficialBookUseCases):
    def __init__(self, books: list[Book]) -> None:
        self.books = books

    async def fetch_books(self, client=None) -> list[Book]:
        return list(self.books)


class FakeNonOfficialBookUseCases(NonOfficialBookUseCases):
    def __init__(self, books: list[Book]) -> None:
        self.books = books

    async def fetch_books(self, client=None) -> list[Book]:
        return list(self.books)
