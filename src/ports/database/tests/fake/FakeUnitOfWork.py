from ports.database import IBookPriceRepository, IBookRepository, IDbContext, IUnitOfWork
from ports.database.tests.fake.FakeBookPriceRepository import FakeBookPriceRepository
from ports.database.tests.fake.FakeBookRepository import FakeBookRepository
from ports.database.tests.fake.FakeDbContext import FakeDbContext


class FakeUnitOfWork(IUnitOfWork):
    context: IDbContext
    books: IBookRepository
    prices: IBookPriceRepository

    def __init__(
        self,
        prices: FakeBookPriceRepository | None = None,
        books: FakeBookRepository | None = None,
        context: FakeDbContext | None = None,
    ) -> None:
        self.db_context = context or FakeDbContext()
        self.book_repository = books or FakeBookRepository()
        self.price_repository = prices or FakeBookPriceRepository()
        self.context = self.db_context
        self.books = self.book_repository
        self.prices = self.price_repository

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    async def begin_transaction(self, transaction_name: str) -> None:
        pass

    async def commit_transaction(self) -> None:
        pass

    async def rollback_transaction(self) -> None:
        pass
