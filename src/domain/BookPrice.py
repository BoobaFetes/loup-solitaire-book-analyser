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
