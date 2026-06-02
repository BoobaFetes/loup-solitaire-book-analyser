from pydantic import BaseModel, Field, model_validator

from domain.BookPrice import BookPrice


class Book(BaseModel):
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

    id: int = Field(default=0)
    url: str
    isbn: str
    numero: int
    titre: str
    authors: list[str] = Field(default_factory=lambda: [])
    lastParutionDate: str  # iso format date string, e.g. "2022-06-16"
    description: str
    official: bool
    prices: list[BookPrice] = Field(default_factory=lambda: [])
    image: str

    @model_validator(mode="after")
    def set_id_from_numero(self) -> "Book":
        """Sets the ID of the book from its numero if ID is not already set.

        Returns:
            Book: The updated book instance.
        """
        if self.id == 0:
            self.id = self.numero
        return self

    def __str__(self) -> str:
        return f"[ISBN: {self.isbn:>13}] [image: {'true' if self.image else 'false':<5}] {self.numero:>3}. {self.titre:<40} ({self.url:<120}) [parution date: {self.lastParutionDate}] [authors: {', '.join(self.authors)}]"

    def add_price(self, price: BookPrice):
        """Adds a price to the book's list of prices.

        Args:
            price (BookPrice): The price to add.
        """
        self.prices.append(price)

    # region equality and hashing based on id to ensure that books with the same numero are considered equal (uses of Set type)
    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.id == other.id

    # endregion
