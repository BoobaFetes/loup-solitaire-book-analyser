from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.sqlalchemy.entities.EntityBase import EntityBase

if TYPE_CHECKING:
    from persistence.sqlalchemy.entities.AuthorEntity import AuthorEntity
    from persistence.sqlalchemy.entities.BookEntity import BookEntity


class BookAuthorEntity(EntityBase):
    __tablename__ = "book_author"

    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    book: Mapped["BookEntity"] = relationship(back_populates="authors")
    author: Mapped["AuthorEntity"] = relationship(back_populates="books")
