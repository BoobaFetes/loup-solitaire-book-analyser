import asyncio
from datetime import date
from typing import cast

from sqlalchemy.pool import StaticPool

from adapters.database.sqlalchemy.BookPriceRepository import BookPriceRepository
from adapters.database.sqlalchemy.BookRepository import BookRepository
from adapters.database.sqlalchemy.DbContext import DbContext
from adapters.database.sqlalchemy.tests.fake import FakeDbContext
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

    # Arrange
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

    # Act
    stored, listed, fetched = asyncio.run(scenario())

    # Assert
    assert stored is not None
    assert stored.isbn == "9782075168694"
    assert stored.authors == ["Joe Dever", "Gary Chalk"]
    actual = len(stored.prices)

    expected = 1
    assert actual == expected
    assert listed == [stored]
    assert fetched == stored


def test_unit_of_work_transaction_can_be_rolled_back():

    # Arrange
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

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = []
    assert actual == expected


def test_unit_of_work_transaction_can_be_committed():

    # Arrange
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

    # Act
    actual = asyncio.run(scenario())

    # Assert
    assert [(price.source, price.price) for price in actual] == [
        ("https://example.test", 12.5),
        ("https://second.test", 10.0),
    ]


def test_book_repository_filters_add_update_and_many_operations():

    # Arrange
    async def scenario():
        context = make_context()
        books = BookRepository(context)
        try:
            first = sample_book(1, "isbn-1")
            second = sample_book(2, "isbn-2")
            second.titre = "Second livre"
            second.lastParutionDate = "2024-02-03"

            added = await books.add(second)
            add_many = await books.add_many([first])
            updated = await books.update(
                Book(
                    id=2,
                    url="https://example.test/updated",
                    isbn="isbn-2",
                    numero=22,
                    titre="Second livre modifie",
                    authors=[],
                    lastParutionDate=date(2024, 2, 4),
                    description="updated",
                    official=False,
                    image="updated-cover",
                    acquired=True,
                )
            )
            missing_update = await books.update(sample_book(99, "missing"))
            upserted_by_isbn = await books.upsert(
                Book(
                    id=3,
                    url="https://example.test/rekeyed",
                    isbn="isbn-1",
                    numero=3,
                    titre="Updated by ISBN",
                    authors=["Joe Dever"],
                    lastParutionDate=date(2024, 3, 1),
                )
            )
            filtered_by_id = await books.list({"id": 2})
            filtered_by_isbn = await books.list({"isbn": "isbn-1"})
            filtered_by_title = await books.list({"titre": "Second livre modifie"})
            filtered_by_numero = await books.list({"numero": 22})
            missing_get = await books.get(404)

            return (
                added,
                add_many,
                updated,
                missing_update,
                upserted_by_isbn,
                filtered_by_id,
                filtered_by_isbn,
                filtered_by_title,
                filtered_by_numero,
                missing_get,
            )
        finally:
            context.engine.dispose()

    # Act
    (
        added,
        add_many,
        updated,
        missing_update,
        upserted_by_isbn,
        filtered_by_id,
        filtered_by_isbn,
        filtered_by_title,
        filtered_by_numero,
        missing_get,
    ) = asyncio.run(scenario())

    # Assert
    assert added is not None
    assert added.lastParutionDate == date(2024, 2, 3)
    assert [book.isbn for book in add_many] == ["isbn-1"]
    assert updated is not None
    assert updated.titre == "Second livre modifie"
    assert updated.acquired is True
    assert missing_update is None
    assert upserted_by_isbn is not None
    assert upserted_by_isbn.id == 3
    assert [book.id for book in filtered_by_id] == [2]
    assert [book.titre for book in filtered_by_isbn] == ["Updated by ISBN"]
    assert [book.id for book in filtered_by_title] == [2]
    assert [book.id for book in filtered_by_numero] == [2]
    assert missing_get is None


def test_book_price_repository_filters_and_last_prices_by_source():

    # Arrange
    async def scenario():
        context = make_context()
        prices = BookPriceRepository(context)
        try:
            first = BookPrice(
                isbn="isbn-1",
                source="source-a",
                date=date(2024, 1, 1),
                price=10.0,
                url="https://a/old",
                currency="EUR",
            )
            latest = BookPrice(
                isbn="isbn-1",
                source="source-a",
                date=date(2024, 1, 2),
                price=12.0,
                url="https://a/new",
                currency="EUR",
            )
            other = BookPrice(
                isbn="isbn-2",
                source="source-b",
                date=date(2024, 1, 3),
                price=8.0,
                url="https://b",
                currency="EUR",
            )

            added_many = await prices.add_many([first, latest])
            added = await prices.add(other)
            listed = await prices.list()
            by_isbn = await prices.list({"isbn": "isbn-1"})
            by_source = await prices.list({"source": "source-b"})
            by_date = await prices.list({"date": "2024-01-02"})
            fetched = await prices.get(("isbn-1", "source-a", date(2024, 1, 2)))
            missing = await prices.get(("isbn-x", "source-x", date(2024, 1, 1)))
            dict_by_isbn = await prices.dict_by_isbns(["isbn-1"])
            last_by_source = await prices.dict_last_price_of_source_by_isbns(
                ["source-a", "source-b", "missing-source"],
                ["isbn-1", "isbn-2", "isbn-3"],
            )
            updated = await prices.update(
                BookPrice(
                    isbn="isbn-2",
                    source="source-b",
                    date=date(2024, 1, 3),
                    price=9.5,
                    url="https://b/updated",
                    currency="USD",
                )
            )
            missing_update = await prices.update(
                BookPrice(
                    isbn="isbn-x",
                    source="source-x",
                    date=date(2024, 1, 1),
                    price=1.0,
                    url="https://missing",
                    currency="EUR",
                )
            )
            upserted_many = await prices.upsert_many([first])

            return (
                added_many,
                added,
                listed,
                by_isbn,
                by_source,
                by_date,
                fetched,
                missing,
                dict_by_isbn,
                last_by_source,
                updated,
                missing_update,
                upserted_many,
            )
        finally:
            context.engine.dispose()

    # Act
    (
        added_many,
        added,
        listed,
        by_isbn,
        by_source,
        by_date,
        fetched,
        missing,
        dict_by_isbn,
        last_by_source,
        updated,
        missing_update,
        upserted_many,
    ) = asyncio.run(scenario())

    # Assert
    assert [(price.isbn, price.date) for price in added_many] == [
        ("isbn-1", date(2024, 1, 1)),
        ("isbn-1", date(2024, 1, 2)),
    ]
    assert added is not None
    actual = len(listed)

    expected = 3
    assert actual == expected
    assert [price.date for price in by_isbn] == [date(2024, 1, 1), date(2024, 1, 2)]
    assert [price.isbn for price in by_source] == ["isbn-2"]
    assert [price.price for price in by_date] == [12.0]
    assert fetched is not None
    assert fetched.price == 12.0
    assert fetched.url == "https://a/new"
    assert missing is None
    actual = list(dict_by_isbn)

    expected = ["isbn-1"]
    assert actual == expected
    assert [price.date for price in dict_by_isbn["isbn-1"]] == [
        date(2024, 1, 1),
        date(2024, 1, 2),
    ]
    assert last_by_source["isbn-1"]["source-a"] is not None
    assert last_by_source["isbn-1"]["source-a"].price == 12.0
    assert last_by_source["isbn-1"]["source-b"] is None
    assert last_by_source["isbn-3"]["missing-source"] is None
    assert updated is not None
    assert updated.price == 9.5
    assert updated.currency == "USD"
    assert missing_update is None
    assert [(price.isbn, price.source, price.date) for price in upserted_many] == [
        ("isbn-1", "source-a", date(2024, 1, 1))
    ]


def test_book_repository_returns_fallback_values_when_context_fails():

    # Arrange
    async def scenario():
        books = BookRepository(cast(DbContext, FakeDbContext()))
        entity = sample_book()

        return (
            await books.list(),
            await books.get(1),
            await books.add(entity),
            await books.upsert(entity),
            await books.update(entity),
            await books.add_many([entity]),
            await books.upsert_many([entity]),
            await books.update_many([entity]),
        )

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = ([], None, None, None, None, [], [], [])
    assert actual == expected


def test_book_price_repository_returns_fallback_values_when_context_fails():

    # Arrange
    async def scenario():
        prices = BookPriceRepository(cast(DbContext, FakeDbContext()))
        entity = BookPrice(
            isbn="isbn",
            source="source",
            date=date(2024, 1, 1),
            price=1.0,
            url="https://example.test",
            currency="EUR",
        )

        return (
            await prices.dict_by_isbns(["isbn"]),
            await prices.dict_last_price_of_source_by_isbns(["source"], ["isbn"]),
            await prices.list(),
            await prices.get(("isbn", "source", date(2024, 1, 1))),
            await prices.add(entity),
            await prices.upsert(entity),
            await prices.update(entity),
            await prices.add_many([entity]),
            await prices.upsert_many([entity]),
            await prices.update_many([entity]),
        )

    # Act
    actual = asyncio.run(scenario())

    # Assert
    expected = (
        {},
        {},
        [],
        None,
        None,
        None,
        None,
        [],
        [],
        [],
    )
    assert actual == expected
