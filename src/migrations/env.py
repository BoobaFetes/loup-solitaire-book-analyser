import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from persistence.sqlalchemy.entities.AuthorEntity import AuthorEntity
from persistence.sqlalchemy.entities.BookAuthorEntity import BookAuthorEntity
from persistence.sqlalchemy.entities.BookEntity import BookEntity
from persistence.sqlalchemy.entities.BookPriceEntity import BookPriceEntity
from persistence.sqlalchemy.entities.EntityBase import EntityBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = EntityBase.metadata

# C’est une astuce volontaire pour Alembic en code first.
# target_metadata = EntityBase.metadata ne contient que les tables des classes SQLAlchemy qui ont été importées au moins une fois par Python.
_loaded_entities = (
    AuthorEntity,
    BookAuthorEntity,
    BookEntity,
    BookPriceEntity,
)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def _set_database_url() -> None:
    connection_string = os.getenv("CONNECTION_STRING_MIGRATION")
    if not connection_string:
        raise RuntimeError(
            "CONNECTION_STRING_MIGRATION environment variable is required"
        )
    config.set_main_option("sqlalchemy.url", connection_string)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
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
