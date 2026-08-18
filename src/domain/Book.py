from dataclasses import dataclass, field
from datetime import date

from domain.BookPrice import BookPrice


@dataclass
class Book:
    """Represents a book entity.

    id: the unique identifier of the book, set to 0 by default and will be updated from numero if not set.

    url: the URL of the book's page.

    isbn: the ISBN of the book.

    numero: the numero of the book, used to set the ID if ID is not already set. Can be negative if the number of the book is not found in the url

    titre: the title of the book.

    authors: the list of authors of the book.

    image: the image in base64 format.

    description: the description of the book.

    official: whether the book is official or not.

    prices: the list of prices for the book.

    Args:
        BaseModel: The base model class from Pydantic.
    """

    id: int = 0
    url: str = ""
    isbn: str = ""
    numero: int = 0
    titre: str = ""
    authors: list[str] = field(default_factory=list)
    lastParutionDate: date | str = date.min
    description: str = ""
    official: bool = False
    prices: list[BookPrice] = field(default_factory=list)
    image: str = ""
    acquired: bool = False

    def __str__(self) -> str:
        return f"[ISBN: {self.isbn:>13}] [image: {'true' if self.image else 'false':<5}] {self.numero:>3}. {self.titre:<40} ({self.url:<100}) [parution date: {self.lastParutionDate}] [authors: {', '.join(self.authors)}]"

    def add_prices(self, prices: list[BookPrice]):
        """Adds multiple prices to the book's list of prices.

        Args:
            prices (list[BookPrice]): The prices to add.
        """
        for price in prices:
            self.add_price(price)

    def add_price(self, price: BookPrice) -> bool:
        """Adds a price to the book's list of prices.

        Args:
            price (BookPrice): The price to add.
        """
        if price in self.prices:
            return False

        self.prices.append(price)
        return True

    # region equality and hashing based on id to ensure that books with the same numero are considered equal (uses of Set type)
    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            raise TypeError(f"Cannot compare Book with {type(other)}")

        return self.id == other.id

    # endregion
