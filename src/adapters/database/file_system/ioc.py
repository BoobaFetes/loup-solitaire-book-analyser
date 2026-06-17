from dependency_injector import providers

from adapters.database.file_system import (
    BookFileRepository,
    BookPriceFileRepository,
    Database,
    DbContext,
)
from adapters.database.UnitOfWork import UnitOfWork
from ports.os import IFileSystem


def make_unit_of_work(
    fs: IFileSystem,
    config: providers.Configuration,
) -> providers.Singleton[UnitOfWork]:
    database = providers.Singleton(
        Database,
        fs=fs,
        connection_string=config.connection_string,
    )
    context = providers.Singleton(
        DbContext,
        db=database,
    )
    prices = providers.Singleton(
        BookPriceFileRepository,
        db=database,
    )
    books = providers.Singleton(
        BookFileRepository,
        db=database,
        prices=prices,
    )

    return providers.Singleton(UnitOfWork, context=context, books=books, prices=prices)
