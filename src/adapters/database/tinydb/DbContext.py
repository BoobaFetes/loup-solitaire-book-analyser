import logging
from pathlib import Path

from tinydb import TinyDB
from tinydb.table import Table

from ports.database import IDbContext


class DbContext(IDbContext):
    @property
    def books(self) -> Table:
        return self.__store.table("books")

    @property
    def prices(self) -> Table:
        return self.__store.table("prices")

    def __init__(self, connection_string: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        directory = Path(connection_string)
        directory.mkdir(parents=True, exist_ok=True)

        self.__store_path: Path = directory / "store.json"
        self.__store: TinyDB = TinyDB(
            self.__store_path,
            indent=4,
            ensure_ascii=False,
        )

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        """
        Start the database context.
        """
        self.__logger.info(f"Open TinyDB Database at {self.__store_path}")

    async def stop(self):
        """
        Stop the database context.
        """
        self.__logger.info(f"Close TinyDB Database at {self.__store_path}")

    async def begin_transaction(self, transaction_name: str):
        pass

    async def commit_transaction(self):
        pass

    async def rollback_transaction(self):
        pass
