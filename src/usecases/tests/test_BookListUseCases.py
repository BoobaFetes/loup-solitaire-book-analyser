import asyncio

from domain import Book
from ports.database import IBookPriceRepository, IBookRepository, IUnitOfWork
from ports.http import HttpClientBase
from usecases.BookListUseCases import BookListUseCases
from usecases.book import NonOfficialBookUseCases, OfficialBookUseCases


def make_book(
    numero: int,
    titre: str,
    isbn: str,
    *,
    official: bool,
    url: str = "",
) -> Book:
    return Book(
        id=numero,
        url=url or f"https://example.test/{isbn}",
        isbn=isbn,
        numero=numero,
        titre=titre,
        authors=["Joe Dever"],
        official=official,
    )


class FakeHttpClient(HttpClientBase[object, object]):
    async def open(self, **kwargs) -> None:
        pass

    async def close(self) -> None:
        pass


class FakeBookRepository(IBookRepository):
    def __init__(self) -> None:
        self.items: list[Book] = []
        self.upserted_items: list[Book] = []

    async def list(self, filters={}) -> list[Book]:
        return list(self.items)

    async def get(self, id: int) -> Book | None:
        return next((book for book in self.items if book.id == id), None)

    async def upsert_many(self, entities: list[Book]) -> list[Book]:
        self.upserted_items = list(entities)
        self.items = list(entities)
        return list(entities)

    async def upsert(self, entity: Book) -> Book | None:
        return entity

    async def add_many(self, entities: list[Book]) -> list[Book]:
        return entities

    async def add(self, entity: Book) -> Book | None:
        return entity

    async def update_many(self, entities: list[Book]) -> list[Book]:
        return entities

    async def update(self, entity: Book) -> Book | None:
        return entity


class FakeBookPriceRepository(IBookPriceRepository):
    async def list(self, filters={}) -> list:
        return []

    async def get(self, id: tuple[str, str]):
        return None

    async def upsert_many(self, entities: list) -> list:
        return entities

    async def upsert(self, entity):
        return entity

    async def add_many(self, entities: list) -> list:
        return entities

    async def add(self, entity):
        return entity

    async def update_many(self, entities: list) -> list:
        return entities

    async def update(self, entity):
        return entity

    async def dict_last_price_of_source_by_isbns(self, sources: list[str], isbns=[]):
        return {}

    async def dict_by_isbns(self, isbns=[]):
        return {}


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self.books = FakeBookRepository()
        self.prices = FakeBookPriceRepository()
        self.context = None

    async def __aenter__(self) -> IUnitOfWork:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    async def begin_transaction(self, transaction_name: str) -> None:
        pass

    async def commit_transaction(self) -> None:
        pass

    async def rollback_transaction(self) -> None:
        pass


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


def test_fetch_books_merges_sources_fixes_first_title_sorts_and_persists():
    official_books = [
        make_book(2, "La Traversee infernale", "9782075123181", official=True),
        make_book(1, "Les Maitres des tenebres", "9782075168694", official=True),
    ]
    non_official_books = [
        make_book(1, "Les Maîtres des Ténèbres", "9782075168694", official=False),
        make_book(
            25,
            "Sur la Piste du Loup",
            "2070519031",
            official=False,
            url="https://www.bibliotheque-des-aventuriers.com/serie/loup_solitaire/25_piste_loup.htm",
        ),
    ]
    unit_of_work = FakeUnitOfWork()
    use_cases = BookListUseCases(
        unit_of_work,
        FakeHttpClient(),
        FakeOfficialBookUseCases(official_books),
        FakeNonOfficialBookUseCases(non_official_books),
    )

    books = asyncio.run(use_cases.fetch_books())

    assert [book.numero for book in books] == [1, 2, 25]
    assert books[0].titre == "Les Maîtres des Ténèbres"
    assert books[-1].isbn == "2070519031"
    assert books[-1].official is False
    assert unit_of_work.books.upserted_items == books
