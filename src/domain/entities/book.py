from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator

from domain.entities.book_price import BookPrice


class Book(BaseModel):
    id: int = Field(default=0)
    numero: int
    titre: str
    titre_original: str
    description: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prices: list[BookPrice] = Field(default_factory=list)

    @model_validator(mode="after")
    def set_id_from_numero(self) -> "Book":
        if self.id == 0:
            self.id = self.numero
        return self
