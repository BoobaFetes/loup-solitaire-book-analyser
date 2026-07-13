import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from persistence.sqlalchemy.entities.AuthorEntity import AuthorEntity
from persistence.sqlalchemy.entities.BookAcquiredEntity import BookAcquiredEntity
from persistence.sqlalchemy.entities.BookEntity import BookEntity
from persistence.sqlalchemy.entities.BookPriceEntity import BookPriceEntity
from persistence.sqlalchemy.entities.DbProbeEntity import DbProbeEntity
from persistence.sqlalchemy.entities.EntityBase import EntityBase

config = context.config

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = EntityBase.metadata

_loaded_entities = (
    AuthorEntity,
    BookAcquiredEntity,
    BookEntity,
    BookPriceEntity,
    DbProbeEntity,
)


def _set_database_url() -> None:
    connection_string = os.getenv("CONNECTION_STRING_MIGRATION")
    if not connection_string:
        raise RuntimeError(
            "CONNECTION_STRING_MIGRATION environment variable is required"
        )
    config.set_main_option("sqlalchemy.url", connection_string)


def run_migrations_offline() -> None:
    _set_database_url()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    _set_database_url()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
