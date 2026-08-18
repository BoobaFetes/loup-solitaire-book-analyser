from adapters.database.sqlalchemy.BookRepository import BookRepository
from adapters.database.sqlalchemy.DbContext import DbContext
from ports.database import IBookPriceRepository


class BookAcquiredRepository(BookRepository):
    def __init__(self, context: DbContext, prices: IBookPriceRepository | None = None):
        super().__init__(context)
