from domain import Book, BookPrice


class FakeDatabase:
    def __init__(
        self,
        books: dict[str, Book] | None = None,
        prices: dict[str, list[BookPrice]] | None = None,
    ) -> None:
        self.books = books or {}
        self.prices = prices or {}
        self.calls: list[str] = []

    async def start(self) -> None:
        self.calls.append("start")

    async def stop(self) -> None:
        self.calls.append("stop")

    async def read_book_store(self) -> dict[str, Book]:
        return self.books

    async def write_book_store(self, data: dict[str, Book]) -> None:
        self.books = data

    async def read_price_store(self) -> dict[str, list[BookPrice]]:
        return self.prices

    async def write_price_store(self, data: dict[str, list[BookPrice]]) -> None:
        self.prices = data
