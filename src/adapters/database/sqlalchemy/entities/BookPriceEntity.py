import datetime as dt

from sqlalchemy import Date, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from adapters.database.sqlalchemy.entities.EntityBase import EntityBase


class BookPriceEntity(EntityBase):
    __tablename__ = "book_price"

    isbn: Mapped[str] = mapped_column(String(13), primary_key=True)
    source: Mapped[str] = mapped_column(String(100), primary_key=True)
    date: Mapped[dt.date] = mapped_column(
        Date,
        primary_key=True,
        default=dt.datetime.now(dt.timezone.utc).date,
    )
    price: Mapped[float] = mapped_column(Float, default=0.0)
    url: Mapped[str] = mapped_column(String(500))
    currency: Mapped[str] = mapped_column(String(1))
