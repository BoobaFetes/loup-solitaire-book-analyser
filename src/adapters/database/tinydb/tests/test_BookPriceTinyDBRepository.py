import asyncio
from datetime import date
from typing import Protocol, cast

from adapters.database.tinydb.BookPriceTinyDBRepository import BookPriceTinyDBRepository
from adapters.database.tinydb.DbContext import DbContext
from domain import BookPrice
from ports.database import IBookPriceRepository


class BookPriceRepositoryFactory(Protocol):
    def __call__(self, context: DbContext) -> IBookPriceRepository: ...


def make_price(isbn="isbn", source="source", day=date(2026, 1, 1), amount=10.0):
    return BookPrice(isbn=isbn, source=source, date=day, price=amount, url="u", currency="EUR")


def test_upsert_get_list_and_dict_queries(tmp_path):
    async def scenario():
        context = DbContext(str(tmp_path))
        factory = cast(BookPriceRepositoryFactory, BookPriceTinyDBRepository)
        repository = factory(context)
        old = make_price(day=date(2025, 1, 1), amount=9.0)
        new = make_price(day=date(2026, 1, 1), amount=12.0)
        other = make_price(isbn="other", source="amazon")

        await repository.upsert_many([old, new, other])

        return (
            await repository.get(("isbn", "source", date(2026, 1, 1))),
            await repository.list({"isbn": "isbn"}),
            await repository.dict_by_isbns(["isbn"]),
            await repository.dict_last_price_of_source_by_isbns(["source", "amazon"], ["isbn", "missing"]),
        )

    item, listed, by_isbn, last = asyncio.run(scenario())

    assert item is not None
    assert item.price == 12.0
    assert len(listed) == 2
    assert by_isbn["isbn"][0].isbn == "isbn"
    last_source_price = last["isbn"]["source"]
    assert last_source_price is not None
    assert last_source_price.price == 12.0
    assert last["isbn"]["amazon"] is None
    assert last["missing"]["source"] is None
