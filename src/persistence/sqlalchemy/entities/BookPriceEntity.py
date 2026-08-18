import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.sqlalchemy.entities.EntityBase import EntityBase

if TYPE_CHECKING:
    from persistence.sqlalchemy.entities.BookEntity import BookEntity


class BookPriceEntity(EntityBase):
    __tablename__ = "book_price"

    isbn: Mapped[str] = mapped_column(
        String(13),
        ForeignKey("book.isbn", ondelete="CASCADE"),
        primary_key=True,
    )
    source: Mapped[str] = mapped_column(String(100), primary_key=True)
    date: Mapped[dt.date] = mapped_column(
        Date,
        primary_key=True,
        default=dt.datetime.now(dt.timezone.utc).date,
    )
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    url: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="")
    book: Mapped["BookEntity"] = relationship(back_populates="prices")
