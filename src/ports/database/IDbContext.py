from typing import Protocol


class IDbContext(Protocol):
    async def __aenter__(self) -> "IDbContext":
        """
        Enter the runtime context related to this object.
        """
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.
        """
        ...

    async def start(self):
        """
        Start the database context.
        """
        ...

    async def stop(self):
        """
        Stop the database context.
        """
        ...

    async def begin_transaction(self, transaction_name: str):
        """
        Begin a new transaction.

        :param transaction_name: The name of the transaction.

        """
        ...

    async def commit_transaction(self):
        """
        Commit the current transaction.
        """
        ...

    async def rollback_transaction(self):
        """
        Rollback the current transaction.
        """
        ...
