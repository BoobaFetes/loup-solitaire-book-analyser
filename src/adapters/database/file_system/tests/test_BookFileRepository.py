import asyncio
from datetime import date
from typing import Protocol, cast

from adapters.database.file_system.BookFileRepository import BookFileRepository
from adapters.database.file_system.Database import Database
from domain import Book, BookPrice
from ports.database import IBookPriceRepository, IBookRepository, TBookPriceListField


class BookRepositoryFactory(Protocol):
    def __call__(
        self, db: Database, prices: IBookPriceRepository
    ) -> IBookRepository: ...


class FakePriceRepository(IBookPriceRepository):
    def __init__(self):
        self.upserted: list[BookPrice] = []

    async def dict_last_price_of_source_by_isbns(
        self,
        sources: list[str],
        isbns: list[str] = [],
    ) -> dict[str, dict[str, BookPrice | None]]:
        raise NotImplementedError

    async def dict_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        raise NotImplementedError

    async def list(
        self, filters: dict[TBookPriceListField, int | str | bool] = {}
    ) -> list[BookPrice]:
        raise NotImplementedError

    async def get(self, id: tuple[str, str, date]) -> BookPrice | None:
        raise NotImplementedError

    async def upsert_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        self.upserted.extend(entities)
        return entities

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        raise NotImplementedError

    async def add_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        raise NotImplementedError

    async def add(self, entity: BookPrice) -> BookPrice | None:
        raise NotImplementedError

    async def update_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        raise NotImplementedError

    async def update(self, entity: BookPrice) -> BookPrice | None:
        raise NotImplementedError


class FakeDatabase:
    def __init__(self, books: dict[str, Book] | None = None):
        self.books = books or {}

    async def read_book_store(self):
        return self.books

    async def write_book_store(self, data):
        self.books = data


def test_list_filters_books_by_fields():
    book = Book(url="u", isbn="isbn", numero=1, titre="Titre")
    factory = cast(BookRepositoryFactory, BookFileRepository)
    repository = factory(
        cast(Database, FakeDatabase({"1": book})),
        FakePriceRepository(),
    )

    assert asyncio.run(repository.list({"isbn": "isbn"})) == [book]
    assert asyncio.run(repository.list({"isbn": "other"})) == []


def test_upsert_many_stores_books_and_moves_prices_to_price_repository():
    price = BookPrice(isbn="isbn", source="source", price=1.0, url="u", currency="EUR")
    book = Book(url="u", isbn="isbn", numero=1, titre="Titre", prices=[price])
    prices = FakePriceRepository()
    db = FakeDatabase()
    factory = cast(BookRepositoryFactory, BookFileRepository)
    repository = factory(cast(Database, db), prices)

    result = asyncio.run(repository.upsert_many([book]))

    assert result == [book]
    assert db.books["1"].prices == []
    assert prices.upserted == [price]


def test_get_returns_matching_book_or_none():
    book = Book(url="u", isbn="isbn", numero=1, titre="Titre")
    factory = cast(BookRepositoryFactory, BookFileRepository)
    repository = factory(
        cast(Database, FakeDatabase({"1": book})),
        FakePriceRepository(),
    )

    assert asyncio.run(repository.get(1)) == book
    assert asyncio.run(repository.get(2)) is None
