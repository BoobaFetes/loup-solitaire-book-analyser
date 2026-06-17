from dependency_injector import providers

from adapters.database import UnitOfWork
from adapters.database.file_system.DbContext import DbContext
from adapters.database.tinydb import BookPriceTinyDBRepository, BookTinyDBRepository


def make_unit_of_work(
    config: providers.Configuration,
) -> providers.Singleton[UnitOfWork]:
    context = providers.Singleton(
        DbContext,
        connection_string=config.connection_string,
    )
    prices = providers.Singleton(
        BookPriceTinyDBRepository,
        context=context,
    )
    books = providers.Singleton(
        BookTinyDBRepository,
        context=context,
        prices=prices,
    )

    return providers.Singleton(UnitOfWork, context=context, books=books, prices=prices)
