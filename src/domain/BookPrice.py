from datetime import date as Date
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class BookPrice(BaseModel):
    """Represents the price of a book.

        key: isbn + source + date

        it is used to link the price to the book, it is not necessarily unique since a book can have multiple prices from different sources and dates.
    Args:
        BaseModel: The base model class from Pydantic.
    """

    isbn: str = Field(default="")
    source: str
    date: Date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    prix: float
    url: str
    currency: str

    def __str__(self) -> str:
        return f"[date: {self.date}] [source: {self.source:<50}] [ISBN: {self.isbn:>13}] {self.prix:>3} {self.currency} [url: {self.url}]"

    # region equality and hashing based on id to ensure that books with the same numero are considered equal (uses of Set type)
    def __hash__(self) -> int:
        return hash(self.isbn + self.source + str(self.date))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BookPrice):
            raise TypeError(f"Cannot compare BookPrice with {type(other)}")

        return (
            self.isbn == other.isbn
            and self.source == other.source
            and self.date == other.date
        )
