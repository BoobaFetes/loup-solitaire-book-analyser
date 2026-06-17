from ports.database import (
    IBookPriceRepository,
    IBookRepository,
    IDbContext,
    IUnitOfWork,
)


class UnitOfWork(IUnitOfWork):
    """
    Interface for a Unit of Work pattern.
    """

    def __init__(
        self, context: IDbContext, books: IBookRepository, prices: IBookPriceRepository
    ):
        self.context = context
        self.books = books
        self.prices = prices

    async def __aenter__(self) -> "IUnitOfWork":
        await self.context.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.context.stop()

    async def begin_transaction(self, transaction_name: str) -> None:
        await self.context.begin_transaction(transaction_name)

    async def commit_transaction(self) -> None:
        await self.context.commit_transaction()

    async def rollback_transaction(self) -> None:
        await self.context.rollback_transaction()
