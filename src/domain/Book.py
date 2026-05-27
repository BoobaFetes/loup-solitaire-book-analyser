from pydantic import BaseModel, Field, model_validator

from domain.BookPrice import BookPrice


class Book(BaseModel):
    """Represents a book entity.

    Args:
        BaseModel: The base model class from Pydantic.
    """

    id: int = Field(default=0)
    url: str
    isbn: str
    numero: int
    titre: str
    authors: list[str] = Field(default_factory=lambda: [])
    description: str
    official: bool
    prices: list[BookPrice] = Field(default_factory=lambda: [])

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
        return (
            f"[ISBN: {self.isbn:>13}] {self.numero:>3}. {self.titre:<30} ({self.url})"
        )

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
