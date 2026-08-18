from typing import TYPE_CHECKING

from sqlalchemy import Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.sqlalchemy.entities.EntityBase import EntityBase

if TYPE_CHECKING:
    from persistence.sqlalchemy.entities.BookAuthorEntity import BookAuthorEntity


class AuthorEntity(EntityBase):
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(200), unique=True, nullable=False)
    books: Mapped[list["BookAuthorEntity"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
