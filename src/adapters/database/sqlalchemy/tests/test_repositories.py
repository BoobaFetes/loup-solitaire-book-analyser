import asyncio
from datetime import date

from sqlalchemy.pool import StaticPool

from adapters.database.sqlalchemy.BookPriceRepository import BookPriceRepository
from adapters.database.sqlalchemy.BookRepository import BookRepository
from adapters.database.sqlalchemy.DbContext import DbContext
from domain import Book, BookPrice
from persistence.sqlalchemy.entities.EntityBase import EntityBase


def make_context() -> DbContext:
    context = DbContext(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    EntityBase.metadata.create_all(context.engine)
    return context


def sample_book(id: int = 1, isbn: str = "9782075168694") -> Book:
    return Book(
        id=id,
        url="https://example.test/book",
        isbn=isbn,
        numero=id,
        titre="Les Maitres des Tenebres",
        authors=["Joe Dever", "Gary Chalk"],
        lastParutionDate=date(2024, 1, 2),
        description="Un livre dont vous etes le heros",
        official=True,
        image="cover",
        acquired=False,
        prices=[
            BookPrice(
                isbn=isbn,
                source="https://example.test",
                date=date(2024, 1, 3),
                price=12.5,
                url="https://example.test/book",
                currency="EUR",
            )
        ],
    )


def test_repository_actions_use_their_own_session_without_transaction():
    async def scenario():
        context = make_context()
        books = BookRepository(context)
        try:
            stored = await books.upsert(sample_book())
            listed = await books.list()
            fetched = await books.get(1)
            return stored, listed, fetched
        finally:
            context.engine.dispose()

    stored, listed, fetched = asyncio.run(scenario())

    assert stored is not None
    assert stored.isbn == "9782075168694"
    assert stored.authors == ["Joe Dever", "Gary Chalk"]
    assert len(stored.prices) == 1
    assert listed == [stored]
    assert fetched == stored


def test_unit_of_work_transaction_can_be_rolled_back():
    async def scenario():
        context = make_context()
        books = BookRepository(context)
        try:
            await context.begin_transaction()
            await books.upsert(sample_book())
            await context.rollback_transaction()
            return await books.list()
        finally:
            context.engine.dispose()

    assert asyncio.run(scenario()) == []


def test_unit_of_work_transaction_can_be_committed():
    async def scenario():
        context = make_context()
        books = BookRepository(context)
        prices = BookPriceRepository(context)
        try:
            await context.begin_transaction()
            await books.upsert(sample_book())
            await prices.upsert(
                BookPrice(
                    isbn="9782075168694",
                    source="https://second.test",
                    date=date(2024, 1, 4),
                    price=10.0,
                    url="https://second.test/book",
                    currency="EUR",
                )
            )
            await context.commit_transaction()

            fetched = await books.get(1)
            return fetched.prices if fetched else []
        finally:
            context.engine.dispose()

    prices = asyncio.run(scenario())

    assert [(price.source, price.price) for price in prices] == [
        ("https://example.test", 12.5),
        ("https://second.test", 10.0),
    ]
