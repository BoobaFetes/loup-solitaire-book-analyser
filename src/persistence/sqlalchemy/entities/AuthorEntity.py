from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from persistence.sqlalchemy.entities.EntityBase import EntityBase


class AuthorEntity(EntityBase):
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
