import logging
from collections.abc import Callable

from adapters.database.file_system.Database import Database
from domain import Book, BookPrice
from ports import (
    IBookPriceRepository,
    IBookRepository,
    TBookListField,
)


class BookFileRepository(IBookRepository):
    """Implémentation d'un dépôt de books basé sur le système de fichiers.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookRepositoryInterface (BookRepositoryInterface): Interface du dépôt de books.
    """

    def __init__(self, db: Database, prices: IBookPriceRepository):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__db: Database = db
        self.__prices: IBookPriceRepository = prices

    async def list(
        self, filters: dict[TBookListField, int | str | bool] = {}
    ) -> list[Book]:
        _id = int(filters.get("id", 0))
        _isbn = str(filters.get("isbn", ""))
        _titre = str(filters.get("titre", ""))
        _numero = int(filters.get("numero", 0))
        try:
            data_stored = await self.__db.read_book_store()

            def equal_id(book: Book) -> bool:
                return not _id or book.id == _id

            def equal_isbn(book: Book) -> bool:
                return not _isbn or book.isbn == _isbn

            def equal_titre(book: Book) -> bool:
                return not _titre or book.titre == _titre

            def equal_numero(book: Book) -> bool:
                return not _numero or book.numero == _numero

            data: list[Book] = list(
                [
                    item
                    for item in data_stored.values()
                    if equal_id(item)
                    and equal_isbn(item)
                    and equal_titre(item)
                    and equal_numero(item)
                ]
            )
            self.__logger.info(
                f"Listed {len(data)} books from file system",
            )
            return data
        except Exception as e:
            self.__logger.error(
                f"Error listing books from file system: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return []

    async def get(self, id: int) -> Book | None:
        """
        Get an entity by its ID.

        :param id: The ID of the entity to be retrieved.
        :return: The entity with the specified ID.
        """
        try:
            data = await self.__db.read_book_store()
            selected = [item for item in data.values() if item.id == id]
            return selected[0] if selected else None
        except Exception as e:
            self.__logger.error(
                f"Error getting book for id '{id}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def upsert_many(self, entities: list[Book]) -> list[Book]:
        try:
            if not entities:
                return []

            data = await self.__db.read_book_store()

            ref = {"count": 0}

            def increment_count():
                ref["count"] += 1

            prices_to_store: list[BookPrice] = []
            for entity in entities:
                self.__upsert_engine(
                    data,
                    prices_to_store,
                    entity,
                    on_add=increment_count,
                    on_update=increment_count,
                )

            await self.__db.write_book_store(data)
            await self.__prices.upsert_many(prices_to_store)

            return entities
        except Exception as e:
            self.__logger.error(
                f"Error upserting books : {type(e).__name__}: {e}",
                exc_info=True,
            )

        return entities

    async def upsert(self, entity: Book) -> Book | None:
        # try:
        #     data = await self.__db.read_book_store()
        #     prices_to_store: list[BookPrice] = []
        #     self.__upsert_engine(
        #         data, prices_to_store, entity, on_add=None, on_update=None
        #     )

        #     await self.__db.write_book_store(data)
        #     await self.__prices.upsert_many(prices_to_store)

        #     return await self.get(entity.id)
        # except Exception as e:
        #     self.__logger.error(
        #         f"Error upserting book n°'{entity.numero}' (id: {entity.id}): {type(e).__name__}: {e}",
        #         exc_info=True,
        #     )

        # return None
        raise NotImplementedError("upsert is not implemented for BookFileRepository.")

    def __upsert_engine(
        self,
        book_store: dict[str, Book],
        prices: list[BookPrice],
        entity: Book,
        *,
        on_add: Callable[[], None] | None,
        on_update: Callable[[], None] | None,
    ) -> None:
        stored_data = book_store.get(str(entity.id), None)
        if stored_data and stored_data == entity:
            book_store[str(entity.id)] = entity
            prices.extend(entity.prices)
            entity.prices = []
            if on_update:
                on_update()
            return

        # en python, on aurait pu utiliser le for/else mais en terme de lecture ca peut etre piegeux, on utilise la facon utilisé par 99% des devs (tout language confondu)
        book_store[str(entity.id)] = entity
        prices.extend(entity.prices)
        entity.prices = []
        if on_add:
            on_add()
