from datetime import datetime, timezone

from pydantic import BaseModel, Field


class BookPrice(BaseModel):
    id: int = Field(default=0)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prix: float
    source: str
