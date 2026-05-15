from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator


class TomePrice(BaseModel):
    id: int = Field(default=0)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prix: float
    source: str


class Tome(BaseModel):
    id: int = Field(default=0)
    numero: int
    titre: str
    titre_original: str
    description: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prices: list[TomePrice] = Field(default_factory=list)

    @model_validator(mode="after")
    def set_id_from_numero(self) -> "Tome":
        if self.id == 0:
            self.id = self.numero
        return self
