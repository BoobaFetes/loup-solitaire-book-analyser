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

import copy
import logging
from collections.abc import Callable
from sqlite3 import Date
from typing import List

from adapters.database.file_system.Database import Database
from domain import BookPrice
from ports import IBookPriceRepository, TBookPriceListField


class BookPriceFileRepository(IBookPriceRepository):
    """Implémentation d'un dépôt de book prices basé sur le système de fichiers.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookPriceRepositoryInterface (BookPriceRepositoryInterface): Interface du dépôt de book prices.
    """

    def __init__(self, db: Database):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__db: Database = db

    async def dict_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        data = await self.__db.read_price_store()
        if not isbns:
            return data
        return {isbn: data.get(isbn, []) for isbn in isbns}

    async def dict_last_price_of_source_by_isbns(
        self, sources: list[str], isbns: list[str] = []
    ) -> dict[str, dict[str, BookPrice | None]]:
        results: dict[str, dict[str, BookPrice | None]] = {}
        data = await self.__db.read_price_store()
        for isbn in isbns:
            for source in sources:
                source_prices_by_isbn = [
                    price for price in data.get(isbn, []) if price.source == source
                ]
                last_price_of_source = max(
                    source_prices_by_isbn, key=lambda p: p.date, default=None
                )
                if isbn not in results:
                    results[isbn] = {}
                results[isbn][source] = last_price_of_source

        return results

    async def list(
        self, filters: dict[TBookPriceListField, int | str | bool] = {}
    ) -> list[BookPrice]:
        _isbn = str(filters.get("isbn", ""))
        try:
            data_stored = await self.__db.read_price_store()
            data: list[BookPrice] = (
                data_stored.get(_isbn, [])
                if _isbn
                else [item for values in data_stored.values() for item in values]
            )

            _source = str(filters.get("source", ""))
            if _source:
                data = [item for item in data if item.source == _source]

            _date = str(filters.get("date", ""))
            if _date:
                data = [item for item in data if item.date == _date]

            self.__logger.info(
                f"Listed {len(data)} book prices for ISBN '{_isbn}' from file system",
            )
            return data
        except Exception as e:
            self.__logger.error(
                f"Error listing book prices for ISBN {_isbn}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return []

    async def get(self, id: tuple[str, str, Date]) -> BookPrice | None:
        """
        Get an entity by its ID.

        :param id: The ID of the entity to be retrieved.
        :return: The entity with the specified ID.
        """
        _isbn, _source, _date = id
        try:
            data = await self.__db.read_price_store()
            stored_data = data.get(_isbn, [])
            for price in stored_data:
                if price.source == _source and (_date is None or price.date == _date):
                    return price
            return None
        except Exception as e:
            self.__logger.error(
                f"Error getting book price for ISBN '{_isbn}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def upsert_many(self, entities: list[BookPrice]) -> int:
        try:
            if not entities:
                return 0

            data = await self.__db.read_price_store()

            ref = {"count": 0}

            def increment_count():
                ref["count"] += 1

            for entity in entities:
                self.__upsert_engine(
                    data, entity, on_add=increment_count, on_update=increment_count
                )

            await self.__db.write_price_store(data)
            self.__logger.info(f"Upserted {ref['count']} book prices in file system")
            return ref["count"]
        except Exception as e:
            self.__logger.error(
                f"Error upserting book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        try:
            data = await self.__db.read_price_store()

            self.__upsert_engine(data, entity, on_add=None, on_update=None)

            await self.__db.write_price_store(data)

            return await self.get((entity.isbn, entity.source, entity.date))
        except Exception as e:
            self.__logger.error(
                f"Error upserting book price for ISBN '{entity.isbn}' and source '{entity.source}' on date '{entity.date}': {type(e).__name__}: {e}",
                exc_info=True,
            )

        return None

    def __upsert_engine(
        self,
        data: dict[str, list[BookPrice]],
        entity: BookPrice,
        *,
        on_add: Callable[[], None] | None,
        on_update: Callable[[], None] | None,
    ) -> None:
        stored_data = data.get(entity.isbn, [])
        data[entity.isbn] = stored_data

        for i, stored_item in enumerate(stored_data):
            # if self._keys_matches(entity, stored_item, for_operation="update"):
            #    is_update_operation = True
            if stored_item == entity:
                stored_data[i] = entity
                if on_update:
                    on_update()
                return

        # en python, on aurait pu utiliser le for/else mais en terme de lecture ca peut etre piegeux, on utilise la facon utilisé par 99% des devs (tout language confondu)
        stored_data.append(entity)
        if on_add:
            on_add()

    async def add_many(self, entities: List[BookPrice]) -> int:
        try:
            if not entities:
                return 0

            data = await self.__db.read_price_store()

            count = 0
            for price in entities:
                stored_data = data.get(price.isbn, [])
                data[price.isbn] = stored_data

                # if any(
                #     [
                #         data
                #         for data in stored_data
                #         if self._keys_matches(price, data, for_operation="add")
                #     ]
                # ):
                #     continue
                if any([item for item in stored_data if price == item]):
                    continue

                stored_data.append(price)
                count += 1

            await self.__db.write_price_store(data)
            self.__logger.info(f"Added {count} book prices to file system")
            return count
        except Exception as e:
            self.__logger.error(
                f"Error adding book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    async def add(self, entity: BookPrice) -> BookPrice | None:
        try:
            data = await self.__db.read_price_store()
            stored_data = data.get(entity.isbn, [])
            data[entity.isbn] = stored_data

            # if any(
            #     [
            #         data
            #         for data in stored_data
            #         if self._keys_matches(entity, data, for_operation="add")
            #     ]
            # ):
            #     return None
            if any([item for item in stored_data if item == entity]):
                return None

            stored_data.append(entity)
            await self.__db.write_price_store(data)
            self.__logger.info(
                f"Added book price for ISBN {entity.isbn} with source {entity.source} and price {entity.price} {entity.currency} to file system",
                exc_info=True,
            )
            return await self.get((entity.isbn, entity.source, entity.date))

        except Exception as e:
            self.__logger.error(
                f"Error adding book price for ISBN {entity.isbn}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def update_many(self, entities: List[BookPrice]) -> int:
        try:
            if not entities:
                return 0

            data = await self.__db.read_price_store()

            count = 0
            for price in entities:
                stored_data = data.get(price.isbn, [])
                data[price.isbn] = stored_data

                for i, stored_item in enumerate(stored_data):
                    # if self._keys_matches(price, stored_item, for_operation="update"):
                    if price == stored_item:
                        stored_data[i] = price
                        count += 1
                        break

            await self.__db.write_price_store(data)
            self.__logger.info(f"Updated {count} book prices in file system")
            return count
        except Exception as e:
            self.__logger.error(
                f"Error updating book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    async def update(self, entity: BookPrice) -> BookPrice | None:
        try:
            data = await self.__db.read_price_store()

            stored_data = data.get(entity.isbn, [])
            data[entity.isbn] = stored_data

            for i, stored_item in enumerate(stored_data):
                # if self._keys_matches(entity, stored_item, for_operation="update"):
                if entity == stored_item:
                    stored_data[i] = entity
                    break

            await self.__db.write_price_store(data)
            self.__logger.info(
                f"Updated book price for ISBN {entity.isbn} with source {entity.source} and price {entity.price} {entity.currency} in file system",
            )
            return await self.get((entity.isbn, entity.source, entity.date))
        except Exception as e:
            self.__logger.error(
                f"Error updating book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return None

    async def delete(self, id: tuple[str, str, Date]) -> bool:
        """
        Delete an entity from the repository by its ID.

        :param id: The ID of the entity to be deleted.
        """
        try:
            store = await self.__db.read_price_store()
            data = await self.get(id)
            if not data:
                return False

            new_store = copy.deepcopy(store)
            new_store[data.isbn] = [
                item for item in new_store[data.isbn] if data != item
            ]

            await self.__db.write_price_store(new_store)
            return True
        except Exception as e:
            self.__logger.error(
                f"Error removing book {id}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return False

    async def clear(self) -> bool:
        try:
            await self.__db.write_price_store({})
            self.__logger.info("Cleared all book prices from file system")
            return True
        except Exception as e:
            self.__logger.error(
                f"Error clearing book prices: {type(e).__name__}: {e}", exc_info=True
            )
        return False

    # => should not bu used because there is a __eq__ method implemented in the entity model
    # def _keys_matches(
    #     self,
    #     price: BookPrice,
    #     stored_item: BookPrice,
    #     for_operation: Literal["add", "update", "delete"],
    # ) -> bool:

    #     # s'il ne s'agit pas du tout de la meme source et du meme isbn alors ce n'est pas le même item
    #     if not (
    #         price.isbn == stored_item.isbn and price.source == stored_item.source
    #     ):
    #         return False

    #     if for_operation in ["update", "delete"]:
    #         # si la date doit matcher alors on vérifie que c'est le même item en comparant la date
    #         # dans le cas d'une mise à jour ou d'une suppression les 3 clés doivent matcher
    #         return price.date == stored_item.date
    #     elif for_operation == "add":
    #         # dans le cas d'un ajout, la date ne doit pas matcher
    #         return (
    #             price.date != stored_item.date
    #         )  # may be ? set to before=> return True
    #     else:
    #         # vu que l'on utilise pyright pour valider les types, cette condition ne devrait jamais être vérifiée, mais on la laisse pour garantir la robustesse du code en cas de mauvaise utilisation de la méthode
    #         raise ValueError(
    #             f"Invalid operation: {for_operation}. Expected 'add', 'update' or 'delete'."
    #         )
