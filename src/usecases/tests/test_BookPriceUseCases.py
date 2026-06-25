import asyncio
from datetime import date

from domain import Book, BookPrice
from adapters.database.tests.fake import FakeBookPriceRepository, FakeUnitOfWork
from usecases.BookPriceUseCases import BookPriceUseCases
from usecases.price.tests.fake import FakePriceSourceUsecases


def make_book(isbn: str, titre: str = "Livre") -> Book:
    return Book(
        id=1,
        url=f"https://example.test/{isbn}",
        isbn=isbn,
        numero=1,
        titre=titre,
        authors=["Joe Dever"],
    )


def make_price(
    isbn: str,
    source: str,
    price: float,
    currency: str = "€",
    *,
    price_date: date = date(2026, 6, 18),
) -> BookPrice:
    return BookPrice(
        isbn=isbn,
        source=source,
        date=price_date,
        price=price,
        currency=currency,
        url=f"{source}/{isbn}",
    )


def test_fetch_prices_stores_only_new_changed_and_valid_prices():
    books = [make_book("9782075123211"), make_book("2070519031")]
    unchanged = make_price("9782075123211", "https://gallimard.test", 16.5)
    changed = make_price(
        "2070519031",
        "https://amazon.test",
        35.0,
        price_date=date(2026, 6, 17),
    )
    new_amazon_only = make_price("2070519031", "https://amazon.test", 42.0)
    not_set = make_price("9782075123211", "https://missing.test", 0.0, "not set")
    repository = FakeBookPriceRepository(
        last_prices={
            "9782075123211": {"https://gallimard.test": unchanged},
            "2070519031": {"https://amazon.test": changed},
        }
    )
    use_cases = BookPriceUseCases(
        FakeUnitOfWork(repository),
        [
            FakePriceSourceUsecases("https://gallimard.test", [unchanged]),
            FakePriceSourceUsecases("https://amazon.test", [new_amazon_only]),
            FakePriceSourceUsecases("https://missing.test", [not_set]),
        ],
    )

    results = asyncio.run(use_cases.fetch_prices(books))

    assert results == {
        "9782075123211": [unchanged, not_set],
        "2070519031": [new_amazon_only],
    }
    assert repository.upserted_items == [new_amazon_only]


def test_bind_prices_to_books_uses_copies_and_supports_amazon_only_prices():
    book = make_book("2070519031", "Sur la Piste du Loup")
    amazon_price = make_price("2070519031", "https://amazon.test", 42.0)
    repository = FakeBookPriceRepository(
        prices_by_isbn={"2070519031": [amazon_price]}
    )
    use_cases = BookPriceUseCases(FakeUnitOfWork(repository), [])

    results = asyncio.run(use_cases.bind_prices_to_books([book]))

    assert results[0] is not book
    assert results[0].prices == [amazon_price]
    assert book.prices == []
