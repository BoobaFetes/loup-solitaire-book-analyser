import logging

from adapters.database.file_system.Database import Database
from ports import IDbContext


class DbContext(IDbContext):
    def __init__(self, db: Database):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.db = db

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        """
        Start the database context.
        """
        # Initialize the database connection here
        self.__logger.info("Opening db context connection  with file system")
        await self.db.start()

    async def stop(self):
        """
        Stop the database context.
        """
        self.__logger.info("Closing db context connection with file system")
        await self.db.stop()

    async def begin_transaction(self, transaction_name: str):
        pass

    async def commit_transaction(self):
        pass

    async def rollback_transaction(self):
        pass
