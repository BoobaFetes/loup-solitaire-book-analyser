from typing import Protocol

from ports.database.IBookPriceRepository import IBookPriceRepository
from ports.database.IBookRepository import IBookRepository
from ports.database.IDbContext import IDbContext


class IUnitOfWork(Protocol):
    """
    Interface for a Unit of Work pattern.
    """

    context: IDbContext
    books: IBookRepository
    prices: IBookPriceRepository

    async def __aenter__(self) -> "IUnitOfWork":
        """
        Enter the runtime context related to this object.
        """
        ...

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the runtime context related to this object.
        """
        ...

    async def begin_transaction(self, transaction_name: str) -> None:
        """
        Begin a new transaction.

        :param transaction_name: The name of the transaction.
        """
        ...

    async def commit_transaction(self) -> None:
        """
        Commit the current transaction.
        """
        ...

    async def rollback_transaction(self) -> None:
        """
        Rollback the current transaction.
        """
        ...
