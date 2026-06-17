import logging
from datetime import date
from typing import Any

from tinydb import Query
from tinydb.table import Document, Table

from adapters.database.tinydb.DbContext import DbContext
from domain import BookPrice
from ports.database import IBookPriceRepository, TBookPriceListField


class BookPriceTinyDBRepository(IBookPriceRepository):
    """Implémentation d'un dépôt de book prices basé sur TinyDB.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookPriceRepositoryInterface (BookPriceRepositoryInterface): Interface du dépôt de book prices.
    """

    def __init__(self, context: DbContext):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__store: Table = context.prices

    def __to_entities_as_dict(self, data: list[Document]) -> dict[str, list[BookPrice]]:
        result: dict[str, list[BookPrice]] = {}
        for item in data:
            entity = self.__to_entity(item)
            result.setdefault(entity.isbn, []).append(entity)
        return result

    def __to_entities(self, data: list[Document]) -> list[BookPrice]:
        return [self.__to_entity(item) for item in data]

    def __to_entity(self, data: Document) -> BookPrice:
        return BookPrice(**data)

    def __to_document(self, entity: BookPrice) -> dict[str, Any]:
        json_data = entity.model_dump(mode="json")
        return json_data

    async def dict_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        try:
            if not isbns:
                data = self.__store.all()
            else:
                query = Query()
                data = self.__store.search(
                    query.isbn.one_of(isbns) if isbns else query.isbn.exists()
                )

            return self.__to_entities_as_dict(data)
        except Exception as e:
            self.__logger.error(
                f"Error listing book prices by ISBNs: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return {}

    async def dict_last_price_of_source_by_isbns(
        self, sources: list[str], isbns: list[str] = []
    ) -> dict[str, dict[str, BookPrice | None]]:
        try:
            query = Query()
            data = self.__store.search(
                query.isbn.one_of(isbns) & query.source.one_of(sources)
            )

            # action 1: fill with data from database
            results: dict[str, dict[str, BookPrice | None]] = {}
            for entity in self.__to_entities(data):
                results.setdefault(entity.isbn, {})
                results[entity.isbn].setdefault(entity.source, None)
                results[entity.isbn][entity.source] = max(
                    [results[entity.isbn][entity.source], entity],
                    key=lambda p: p.date if p else date.min,
                    default=None,
                )

            # action 2 : add non existing isbn and source with None value to the results
            for isbn in isbns:
                results.setdefault(isbn, {})
                for source in sources:
                    results[isbn].setdefault(source, None)
            return results
        except Exception as e:
            self.__logger.error(
                f"Error listing last book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return {}

    async def list(
        self, filters: dict[TBookPriceListField, int | str | bool] = {}
    ) -> list[BookPrice]:
        _isbn = str(filters.get("isbn", ""))
        _source = str(filters.get("source", ""))
        _date = str(filters.get("date", ""))
        try:
            query = Query()
            data = self.__to_entities(
                self.__store.search(
                    (query.isbn == _isbn if _isbn else query.isbn.exists())
                    & (query.source == _source if _source else query.source.exists())
                    & (query.date == _date if _date else query.date.exists())
                )
            )

            self.__logger.info(
                f"Listed {len(data)} book prices for ISBN='{_isbn}' and source='{_source}' and date='{_date}' from file system",
            )
            return data
        except Exception as e:
            self.__logger.error(
                f"Error listing book prices for ISBN '{_isbn}' and source '{_source}' and date '{_date}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return []

    async def get(self, id: tuple[str, str, date]) -> BookPrice | None:
        """
        Get an entity by its ID.

        :param id: The ID of the entity to be retrieved.
        :return: The entity with the specified ID.
        """
        _isbn, _source, _date = id
        try:
            query = Query()
            data = self.__to_entities(
                self.__store.search(
                    (query.isbn == _isbn)
                    & (query.source == _source)
                    & (query.date == _date.isoformat())
                )
            )
            if not data:
                self.__logger.info(
                    f"No book price found for ISBN '{_isbn}' and source '{_source}' and date '{_date}' in TinyDB"
                )
                return None
            return data[0]
        except Exception as e:
            self.__logger.error(
                f"Error getting book price for ISBN '{_isbn}' and source '{_source}' and date '{_date}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def upsert_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        results: list[BookPrice] = []
        for entity in entities:
            item = await self.upsert(entity)
            if item:
                results.append(item)

        return results

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        try:
            document = self.__to_document(entity)
            id = self.__store.upsert(
                document,
                (Query().isbn == entity.isbn)
                & (Query().source == entity.source)
                & (Query().date == entity.date.isoformat()),
            )
            if not id:
                self.__logger.warning(
                    f"Failed to upsert book price for ISBN '{entity.isbn}' and source '{entity.source}' and date '{entity.date}' in TinyDB"
                )
                return None

            item = await self.get((entity.isbn, entity.source, entity.date))
            if not item:
                self.__logger.warning(
                    f"Failed to retrieve upserted book price for ISBN '{entity.isbn}' and source '{entity.source}' and date '{entity.date}' in TinyDB"
                )
                return None

            return item
        except Exception as e:
            self.__logger.error(
                f"Error upserting book price for ISBN '{entity.isbn}' and source '{entity.source}' on date '{entity.date.isoformat()}': {type(e).__name__}: {e}",
                exc_info=True,
            )

        return None
