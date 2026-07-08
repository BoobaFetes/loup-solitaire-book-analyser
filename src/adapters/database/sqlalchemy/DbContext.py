import logging

from sqlalchemy import create_engine

from ports.database import IDbContext


class DbContext(IDbContext):
    def __init__(
        self, connection_string: str, logging_levels: dict[str, int] = {}, **kwargs
    ):
        self.__logger = logging.getLogger(self.__class__.__name__)
        # configure logging levels for SQLAlchemy loggers
        if "sqlalchemy.engine" in logging_levels:
            logging_levels.setdefault(
                "sqlalchemy.engine", logging_levels["sqlalchemy.engine"]
            )
        if "sqlalchemy.pool" in logging_levels:
            logging_levels.setdefault(
                "sqlalchemy.pool", logging_levels["sqlalchemy.pool"]
            )
        if "sqlalchemy.dialects" in logging_levels:
            logging_levels.setdefault(
                "sqlalchemy.dialects", logging_levels["sqlalchemy.dialects"]
            )
        if "sqlalchemy.orm" in logging_levels:
            logging_levels.setdefault(
                "sqlalchemy.orm", logging_levels["sqlalchemy.orm"]
            )

        # create the SQLAlchemy engine with the provided connection string and additional keyword arguments
        self.engine = create_engine(
            connection_string,
            **kwargs,
            echo=True,
            echo_pool=True,
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
        self.__logger.info(f"Open Postgres Database at {self.engine.url}")
        # heu là je ne sais pas => self.engine.begin()

    async def stop(self):
        """
        Stop the database context.
        """
        self.__logger.info(f"Close TinyDB Database at {self.engine.url}")

    async def begin_transaction(self):
        pass

    async def commit_transaction(self):
        pass

    async def rollback_transaction(self):
        pass
