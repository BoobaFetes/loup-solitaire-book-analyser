from ports.database import (
    IBookPriceRepository,
    IBookRepository,
    IDbContext,
    IUnitOfWork,
)
from adapters.database.tests.fake.FakeBookPriceRepository import FakeBookPriceRepository
from adapters.database.tests.fake.FakeBookRepository import FakeBookRepository
from adapters.database.tests.fake.FakeDbContext import FakeDbContext
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeUnitOfWork(IUnitOfWork, SpyStubFake):
    context: IDbContext
    books: IBookRepository
    prices: IBookPriceRepository

    def __init__(
        self,
        prices: FakeBookPriceRepository | None = None,
        books: FakeBookRepository | None = None,
        context: FakeDbContext | None = None,
    ) -> None:
        SpyStubFake.__init__(self)
        self.db_context = context or FakeDbContext()
        self.book_repository = books or FakeBookRepository()
        self.price_repository = prices or FakeBookPriceRepository()
        self.context = self.db_context
        self.books = self.book_repository
        self.prices = self.price_repository

    def stub_begin_transaction(self, returned: None = None) -> None:
        self._stub("begin_transaction", returned)

    @property
    def spy_begin_transaction(self) -> list[SpyCall]:
        return self._spy("begin_transaction")

    def stub_commit_transaction(self, returned: None = None) -> None:
        self._stub("commit_transaction", returned)

    @property
    def spy_commit_transaction(self) -> list[SpyCall]:
        return self._spy("commit_transaction")

    def stub_rollback_transaction(self, returned: None = None) -> None:
        self._stub("rollback_transaction", returned)

    @property
    def spy_rollback_transaction(self) -> list[SpyCall]:
        return self._spy("rollback_transaction")

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    async def begin_transaction(self) -> None:
        returned = self._returned_or_default("begin_transaction", None)
        return self._record_call("begin_transaction", (), {}, returned)

    async def commit_transaction(self) -> None:
        returned = self._returned_or_default("commit_transaction", None)
        return self._record_call("commit_transaction", (), {}, returned)

    async def rollback_transaction(self) -> None:
        returned = self._returned_or_default("rollback_transaction", None)
        return self._record_call("rollback_transaction", (), {}, returned)
