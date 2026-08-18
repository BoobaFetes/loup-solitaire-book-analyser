from dependency_injector import providers

from adapters.database.sqlalchemy.BookPriceRepository import BookPriceRepository
from adapters.database.sqlalchemy.BookRepository import BookRepository
from adapters.database.sqlalchemy.DbContext import DbContext
from adapters.database.UnitOfWork import UnitOfWork


def make_unit_of_work(
    config: providers.Configuration,
) -> providers.Singleton[UnitOfWork]:
    context = providers.Singleton(
        DbContext,
        connection_string=config.connection_string_batch,
    )
    prices = providers.Singleton(
        BookPriceRepository,
        context=context,
    )
    books = providers.Singleton(
        BookRepository,
        context=context,
    )

    return providers.Singleton(UnitOfWork, context=context, books=books, prices=prices)
