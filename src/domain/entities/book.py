from pydantic import BaseModel, Field, model_validator

from domain.entities.book_price import BookPrice


class Book(BaseModel):
    """Represents a book entity.

    Args:
        BaseModel: The base model class from Pydantic.
    """

    id: int = Field(default=0)
    numero: int
    titre: str
    titre_original: str
    description: str
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
