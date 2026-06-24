import asyncio
from datetime import date

from adapters.database.UnitOfWork import UnitOfWork
from domain import Book, BookPrice
from ports.database import (
    IBookPriceRepository,
    IBookRepository,
    TBookListField,
    TBookPriceListField,
)
from ports.database.tests.fake import FakeRecordingDbContext


class UnusedBookRepository(IBookRepository):
    async def list(
        self, filters: dict[TBookListField, int | str | bool] = {}
    ) -> list[Book]:
        raise NotImplementedError

    async def get(self, id: int) -> Book | None:
        raise NotImplementedError

    async def upsert_many(self, entities: list[Book]) -> list[Book]:
        raise NotImplementedError

    async def upsert(self, entity: Book) -> Book | None:
        raise NotImplementedError

    async def add_many(self, entities: list[Book]) -> list[Book]:
        raise NotImplementedError

    async def add(self, entity: Book) -> Book | None:
        raise NotImplementedError

    async def update_many(self, entities: list[Book]) -> list[Book]:
        raise NotImplementedError

    async def update(self, entity: Book) -> Book | None:
        raise NotImplementedError


class UnusedBookPriceRepository(IBookPriceRepository):
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
        raise NotImplementedError

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


def test_context_manager_starts_and_stops_context():
    async def scenario():
        context = FakeRecordingDbContext()
        unit = UnitOfWork(context, UnusedBookRepository(), UnusedBookPriceRepository())
        async with unit as current:
            assert current is unit
        return context.calls

    assert asyncio.run(scenario()) == [("start", None), ("stop", None)]


def test_transaction_methods_delegate_to_context():
    async def scenario():
        context = FakeRecordingDbContext()
        unit = UnitOfWork(context, UnusedBookRepository(), UnusedBookPriceRepository())
        await unit.begin_transaction("sync")
        await unit.commit_transaction()
        await unit.rollback_transaction()
        return context.calls

    assert asyncio.run(scenario()) == [
        ("begin", "sync"),
        ("commit", None),
        ("rollback", None),
    ]
