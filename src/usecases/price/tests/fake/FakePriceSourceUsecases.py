from domain import Book, BookPrice
from usecases.price.PriceSourceUsecasesBase import PriceSourceUsecasesBase


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
