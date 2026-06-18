import asyncio
from datetime import date

from domain import Book, BookPrice
from ports.database import IBookPriceRepository, IBookRepository, IUnitOfWork
from usecases.BookPriceUseCases import BookPriceUseCases
from usecases.price.PriceSourceUsecasesBase import PriceSourceUsecasesBase


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


class FakePriceSourceUsecases(PriceSourceUsecasesBase):
    def __init__(self, base_url: str, prices: list[BookPrice]) -> None:
        super().__init__(base_url)
        self.prices = prices
        self.requested_books: list[Book] = []

    async def fetch_bookprices(self, books: list[Book]) -> list[BookPrice]:
        self.requested_books = list(books)
        return list(self.prices)

    async def fetch_bookprice(self, book: Book, **kwargs) -> BookPrice | None:
        return next((price for price in self.prices if price.isbn == book.isbn), None)


class FakeBookRepository(IBookRepository):
    async def list(self, filters={}) -> list[Book]:
        return []

    async def get(self, id: int) -> Book | None:
        return None

    async def upsert_many(self, entities: list[Book]) -> list[Book]:
        return entities

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
    def __init__(self, last_prices=None, prices_by_isbn=None) -> None:
        self.last_prices = last_prices or {}
        self.prices_by_isbn = prices_by_isbn or {}
        self.upserted_items: list[BookPrice] = []

    async def list(self, filters={}) -> list[BookPrice]:
        return []

    async def get(self, id: tuple[str, str]) -> BookPrice | None:
        return None

    async def upsert_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        self.upserted_items = list(entities)
        return list(entities)

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        return entity

    async def add_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        return entities

    async def add(self, entity: BookPrice) -> BookPrice | None:
        return entity

    async def update_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        return entities

    async def update(self, entity: BookPrice) -> BookPrice | None:
        return entity

    async def dict_last_price_of_source_by_isbns(
        self, sources: list[str], isbns: list[str] = []
    ) -> dict[str, dict[str, BookPrice | None]]:
        return self.last_prices

    async def dict_by_isbns(
        self, isbns: list[str] = []
    ) -> dict[str, list[BookPrice]]:
        return self.prices_by_isbn


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self, prices: FakeBookPriceRepository) -> None:
        self.books = FakeBookRepository()
        self.prices = prices
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
