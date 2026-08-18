import logging
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.session import SessionTransaction

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
        self.engine: Engine = create_engine(
            connection_string,
            **kwargs,
            echo=True,
            echo_pool=True,
        )
        self.__session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )
        self.__session: Session | None = None
        self.__transaction: SessionTransaction | None = None

    @property
    def session(self) -> Session | None:
        return self.__session

    @contextmanager
    def operation_session(self) -> Iterator[Session]:
        if self.__session is not None:
            yield self.__session
            return

        session = self.__session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

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
        if self.__session is not None:
            await self.rollback_transaction()
        self.__logger.info(f"Close Postgres Database at {self.engine.url}")

    async def begin_transaction(self):
        if self.__session is not None:
            raise RuntimeError("A transaction is already active")

        self.__session = self.__session_factory()
        self.__transaction = self.__session.begin()

    async def commit_transaction(self):
        if self.__session is None or self.__transaction is None:
            raise RuntimeError("No active transaction to commit")

        try:
            self.__transaction.commit()
        finally:
            self.__transaction = None
            self.__session.close()
            self.__session = None

    async def rollback_transaction(self):
        if self.__session is None or self.__transaction is None:
            raise RuntimeError("No active transaction to rollback")

        try:
            self.__transaction.rollback()
        finally:
            self.__transaction = None
            self.__session.close()
            self.__session = None
