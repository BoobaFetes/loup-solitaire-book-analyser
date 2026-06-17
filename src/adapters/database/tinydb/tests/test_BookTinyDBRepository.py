import asyncio
from typing import Protocol, cast

from adapters.database.tinydb.BookTinyDBRepository import BookTinyDBRepository
from adapters.database.tinydb.BookPriceTinyDBRepository import BookPriceTinyDBRepository
from adapters.database.tinydb.DbContext import DbContext
from domain import Book, BookPrice
from ports.database import IBookPriceRepository, IBookRepository


class BookPriceRepositoryFactory(Protocol):
    def __call__(self, context: DbContext) -> IBookPriceRepository: ...


class BookRepositoryFactory(Protocol):
    def __call__(
        self, context: DbContext, prices: IBookPriceRepository
    ) -> IBookRepository: ...


def test_upsert_get_and_list_books_with_prices(tmp_path):
    async def scenario():
        context = DbContext(str(tmp_path))
        price_factory = cast(BookPriceRepositoryFactory, BookPriceTinyDBRepository)
        book_factory = cast(BookRepositoryFactory, BookTinyDBRepository)
        prices = price_factory(context)
        books = book_factory(context, prices)
        price = BookPrice(isbn="isbn", source="source", price=12.0, url="u", currency="EUR")
        book = Book(url="u", isbn="isbn", numero=1, titre="Titre", prices=[price])

        upserted = await books.upsert(book)

        return upserted, await books.get(1), await books.list({"isbn": "isbn"})

    upserted, fetched, listed = asyncio.run(scenario())

    assert upserted is not None
    assert fetched is not None
    assert upserted.prices == [fetched.prices[0]]
    assert fetched.prices[0].price == 12.0
    assert [book.titre for book in listed] == ["Titre"]
