from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Integer, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.sqlalchemy.entities.EntityBase import EntityBase

if TYPE_CHECKING:
    from persistence.sqlalchemy.entities.BookAuthorEntity import BookAuthorEntity
    from persistence.sqlalchemy.entities.BookPriceEntity import BookPriceEntity


class BookEntity(EntityBase):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    titre: Mapped[str] = mapped_column(Unicode(200), nullable=False, default="")
    lastParutionDate: Mapped[date] = mapped_column(
        "last_parution_date",
        Date,
        nullable=False,
        default=date.min,
    )
    description: Mapped[str] = mapped_column(Unicode(4000), nullable=False, default="")
    official: Mapped[bool] = mapped_column(Boolean, default=False)
    image: Mapped[str] = mapped_column(Unicode(500), nullable=False, default="")
    acquired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    authors: Mapped[list["BookAuthorEntity"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
    )
    prices: Mapped[list["BookPriceEntity"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
    )
