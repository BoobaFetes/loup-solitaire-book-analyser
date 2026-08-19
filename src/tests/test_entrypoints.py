import asyncio
from datetime import date

import find_books
import find_prices
from domain import Book, BookPrice
from tests.fake import FakeContainer


def _book(numero: int) -> Book:
    return Book(
        id=numero,
        url=f"https://example.test/{numero}",
        isbn=f"isbn-{numero}",
        numero=numero,
        titre=f"Livre {numero}",
        authors=["Joe Dever"],
        prices=[
            BookPrice(
                isbn=f"isbn-{numero}",
                source="source",
                date=date(2024, 1, numero),
                price=float(numero),
                url=f"https://price.test/{numero}",
                currency="EUR",
            )
        ],
    )


def test_find_books_main_fetches_books_and_flushes_cache(monkeypatch):

    # Arrange
    container = FakeContainer([_book(2), _book(1)])
    monkeypatch.setattr(find_books, "new_ioc_container", lambda script_name: container)
    monkeypatch.setattr(
        find_books, "print_environment_variables", lambda c, logger: None
    )

    # Act
    asyncio.run(find_books.main())

    # Assert
    assert container.cache.flushed is True


def test_find_prices_main_fetches_and_binds_prices_then_flushes_cache(monkeypatch):

    # Arrange
    books = [_book(1), _book(2)]
    container = FakeContainer(books)
    monkeypatch.setattr(find_prices, "new_ioc_container", lambda script_name: container)
    monkeypatch.setattr(
        find_prices, "print_environment_variables", lambda c, logger: None
    )

    # Act
    asyncio.run(find_prices.main())

    # Assert
    assert container.book_prices.fetched_books == books
    assert container.cache.flushed is True
