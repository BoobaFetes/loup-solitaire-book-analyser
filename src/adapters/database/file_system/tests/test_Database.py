import asyncio

from adapters.database.file_system.Database import Database
from domain import Book, BookPrice
from ports.os import IFileSystem


class MemoryFileSystem(IFileSystem):
    def __init__(self):
        self.files: dict[str, str] = {}

    def is_file_exists(self, name: str) -> bool:
        return name in self.files

    def clear(self, pattern: str) -> None:
        self.files.clear()

    def list(self, pattern: str = "*.html") -> list[str]:
        return list(self.files)

    def write_file(self, name: str, content: str, encoding: str = "utf-8") -> None:
        self.files[name] = content

    def read_file(self, name: str) -> str:
        return self.files[name]


def test_start_creates_missing_stores(tmp_path):
    fs = MemoryFileSystem()
    db = Database(fs, str(tmp_path))

    asyncio.run(db.start())

    assert fs.files[str(tmp_path / "books.data.json")] == "{}"
    assert fs.files[str(tmp_path / "prices.data.json")] == "{}"


def test_read_and_write_book_and_price_stores(tmp_path):
    async def scenario():
        fs = MemoryFileSystem()
        db = Database(fs, str(tmp_path))
        book = Book(url="u", isbn="isbn", numero=1, titre="Titre")
        price = BookPrice(isbn="isbn", source="source", price=12.5, url="u", currency="EUR")

        await db.write_book_store({"1": book})
        await db.write_price_store({"isbn": [price]})

        return await db.read_book_store(), await db.read_price_store()

    books, prices = asyncio.run(scenario())

    assert books["1"].titre == "Titre"
    assert prices["isbn"][0].price == 12.5
