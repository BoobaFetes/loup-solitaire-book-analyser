import asyncio
from datetime import date
from typing import Protocol, cast

from adapters.database.file_system.BookPriceFileRepository import BookPriceFileRepository
from adapters.database.file_system.Database import Database
from domain import BookPrice
from ports.database import IBookPriceRepository


class BookPriceRepositoryFactory(Protocol):
    def __call__(self, db: Database) -> IBookPriceRepository: ...


class FakeDatabase:
    def __init__(self, prices: dict[str, list[BookPrice]] | None = None):
        self.prices = prices or {}

    async def read_price_store(self):
        return self.prices

    async def write_price_store(self, data):
        self.prices = data


def price(isbn="isbn", source="source", day=date(2026, 1, 1), amount=10.0):
    return BookPrice(isbn=isbn, source=source, date=day, price=amount, url="u", currency="EUR")


def test_dict_by_isbns_returns_all_or_selected_prices():
    item = price()
    factory = cast(BookPriceRepositoryFactory, BookPriceFileRepository)
    repository = factory(cast(Database, FakeDatabase({"isbn": [item]})))

    assert asyncio.run(repository.dict_by_isbns()) == {"isbn": [item]}
    assert asyncio.run(repository.dict_by_isbns(["isbn", "missing"])) == {
        "isbn": [item],
        "missing": [],
    }


def test_dict_last_price_of_source_by_isbns_keeps_newest_price():
    old = price(day=date(2025, 1, 1), amount=9.0)
    new = price(day=date(2026, 1, 1), amount=12.0)
    factory = cast(BookPriceRepositoryFactory, BookPriceFileRepository)
    repository = factory(cast(Database, FakeDatabase({"isbn": [old, new]})))

    result = asyncio.run(repository.dict_last_price_of_source_by_isbns(["source"], ["isbn"]))

    assert result == {"isbn": {"source": new}}


def test_list_get_and_upsert_many_manage_prices():
    first = price()
    second = price(source="other")
    db = FakeDatabase({"isbn": [first]})
    factory = cast(BookPriceRepositoryFactory, BookPriceFileRepository)
    repository = factory(cast(Database, db))

    assert asyncio.run(repository.list({"isbn": "isbn"})) == [first]
    assert asyncio.run(repository.get(("isbn", "source", date(2026, 1, 1)))) == first

    result = asyncio.run(repository.upsert_many([first, second]))

    assert result == [first, second]
    assert db.prices["isbn"] == [first, second]
