import asyncio
from typing import Protocol, cast

from adapters.database.file_system.BookFileRepository import BookFileRepository
from adapters.database.file_system.Database import Database
from adapters.database.file_system.tests.fake import FakeDatabase
from domain import Book, BookPrice
from ports.database import IBookPriceRepository, IBookRepository
from ports.database.tests.fake import FakePriceRepository


class BookRepositoryFactory(Protocol):
    def __call__(
        self, db: Database, prices: IBookPriceRepository
    ) -> IBookRepository: ...


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
