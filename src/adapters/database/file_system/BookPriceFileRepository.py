import logging
from collections.abc import Callable
from datetime import date as Date

from adapters.database.file_system.Database import Database
from domain import BookPrice
from ports.database import IBookPriceRepository, TBookPriceListField


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

    async def upsert_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        try:
            if not entities:
                return []

            data = await self.__db.read_price_store()

            ref = {"count": 0}

            def increment_count():
                ref["count"] += 1

            for entity in entities:
                self.__upsert_engine(
                    data, entity, on_add=increment_count, on_update=increment_count
                )

            await self.__db.write_price_store(data)

            items = await self.dict_by_isbns([entity.isbn for entity in entities])
            return [item for prices in items.values() for item in prices]
        except Exception as e:
            self.__logger.error(
                f"Error upserting book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return []

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        # try:
        #     data = await self.__db.read_price_store()

        #     self.__upsert_engine(data, entity, on_add=None, on_update=None)

        #     await self.__db.write_price_store(data)

        #     return await self.get((entity.isbn, entity.source, entity.date))
        # except Exception as e:
        #     self.__logger.error(
        #         f"Error upserting book price for ISBN '{entity.isbn}' and source '{entity.source}' on date '{entity.date}': {type(e).__name__}: {e}",
        #         exc_info=True,
        #     )

        # return None
        raise NotImplementedError(
            "upsert is not implemented for BookPriceFileRepository."
        )

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
