"""Gateways: couche d'adaptateurs d'accès aux données (ports/adapters).

Dans la Clean Architecture, le répertoire `gateways` contient les adaptateurs
qui implémentent les interfaces demandées par le domaine/usecases pour
accéder aux données (base, fichiers, API externes, mémoire, etc.).

- BookRepositoryInterface : définit le contrat attendu par les usecases.
- BookFileRepository : implémentation simple utile pour les tests ou
  pour des scénarios sans persistance externe.

Remarque : les usecases dépendent de l'interface (abstraction), pas de cette
implémentation concrète. On peut remplacer BookFileRepository par une
implémentation DB sans modifier le domaine.
"""

import logging
from collections.abc import Callable
from typing import List

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
            if selected:
                return selected[0]
        except Exception as e:
            self.__logger.error(
                f"Error getting book for id '{id}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def upsert_many(self, entities: list[Book]) -> int:
        try:
            if not entities:
                return 0

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

            self.__logger.info(f"Upserted {ref['count']} books in file system")
            return ref["count"]
        except Exception as e:
            self.__logger.error(
                f"Error upserting books : {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    async def upsert(self, entity: Book) -> Book | None:
        try:
            data = await self.__db.read_book_store()
            prices_to_store: list[BookPrice] = []
            self.__upsert_engine(
                data, prices_to_store, entity, on_add=None, on_update=None
            )

            await self.__db.write_book_store(data)
            await self.__prices.upsert_many(prices_to_store)

            return await self.get(entity.id)
        except Exception as e:
            self.__logger.error(
                f"Error upserting book n°'{entity.numero}' (id: {entity.id}): {type(e).__name__}: {e}",
                exc_info=True,
            )

        return None

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

    async def add_many(self, entities: List[Book]) -> int:
        try:
            if not entities:
                return 0

            data = await self.__db.read_book_store()

            count = 0
            prices_to_store: list[BookPrice] = []
            for entity in entities:
                stored_data = data.get(str(entity.id), None)
                if stored_data:
                    continue

                data[str(entity.id)] = entity
                prices_to_store.extend(entity.prices)
                entity.prices = []
                count += 1

            await self.__db.write_book_store(data)
            await self.__prices.upsert_many(prices_to_store)

            self.__logger.info(f"Added {count} books to file system")
            return count
        except Exception as e:
            self.__logger.error(
                f"Error adding books: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    async def add(self, entity: Book) -> Book | None:
        try:
            data = await self.__db.read_book_store()
            stored_data = data.get(str(entity.id), None)
            if stored_data:
                return None

            prices_to_store: list[BookPrice] = entity.prices
            data[str(entity.id)] = entity
            entity.prices = []

            await self.__db.write_book_store(data)
            await self.__prices.upsert_many(prices_to_store)

            return await self.get(entity.id)
        except Exception as e:
            self.__logger.error(
                f"Error adding book n°'{entity.numero}' (id: {entity.id}) in file system: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def update_many(self, entities: List[Book]) -> int:
        try:
            if not entities:
                return 0

            data = await self.__db.read_book_store()
            prices_to_store: list[BookPrice] = []

            count = 0
            for book in entities:
                stored_data = data.get(str(book.id), None)
                if not stored_data:
                    continue

                data[str(book.id)] = book
                prices_to_store.extend(book.prices)
                book.prices = []
                count += 1

            await self.__db.write_book_store(data)
            await self.__prices.upsert_many(prices_to_store)

            self.__logger.info(f"Updated {count} books in file system")
            return count
        except Exception as e:
            self.__logger.error(
                f"Error updating books: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    async def update(self, entity: Book) -> Book | None:
        try:
            data = await self.__db.read_book_store()

            stored_data = data.get(str(entity.id), None)
            if not stored_data:
                return None

            data[str(entity.id)] = entity
            prices_to_store: list[BookPrice] = entity.prices
            entity.prices = []

            await self.__db.write_book_store(data)
            await self.__prices.upsert_many(prices_to_store)

            self.__logger.info(
                f"Updated book n°'{entity.numero}' (id: {entity.id}) in file system",
            )
            return await self.get(entity.id)
        except Exception as e:
            self.__logger.error(
                f"Error updating book n°'{entity.numero}' (id: {entity.id}) in file system: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return None

    async def delete(self, id: int) -> bool:
        """
        Delete an entity from the repository by its ID.

        :param id: The ID of the entity to be deleted.
        """
        try:
            data = await self.get(id)
            if not data:
                return False

            store = await self.__db.read_book_store()
            del store[str(data.id)]

            await self.__db.write_book_store(store)
            for price in data.prices:
                await self.__prices.delete((price.isbn, price.source, price.date))
            return True
        except Exception as e:
            self.__logger.error(
                f"Error removing book id: {id}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return False

    async def clear(self) -> bool:
        try:
            await self.__db.write_book_store({})
            await self.__prices.clear()
            self.__logger.info("Cleared all books from file system")
            return True
        except Exception as e:
            self.__logger.error(
                f"Error clearing books: {type(e).__name__}: {e}", exc_info=True
            )
        return False
