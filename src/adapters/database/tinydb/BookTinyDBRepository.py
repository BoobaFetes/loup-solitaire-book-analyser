import copy
import logging
from typing import Any, cast

from tinydb import Query
from tinydb.table import Document, Table

from adapters.database.tinydb.DbContext import DbContext
from domain import Book, BookPrice
from ports.database import (
    IBookPriceRepository,
    IBookRepository,
    TBookListField,
)


class BookTinyDBRepository(IBookRepository):
    """Implémentation d'un dépôt de books basé sur TinyDB.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookRepositoryInterface (BookRepositoryInterface): Interface du dépôt de books.
    """

    def __init__(self, context: DbContext, prices: IBookPriceRepository):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__store: Table = context.books
        self.__prices: IBookPriceRepository = prices

    def __to_entities(self, data: list[Document]) -> list[Book]:
        return [self.__to_entity(item) for item in data]

    def __to_entity(self, data: Document) -> Book:
        return Book(**data)

    def __to_document(self, entity: Book) -> dict[str, Any]:
        json_data = entity.model_dump(mode="json")
        return json_data

    async def list(
        self, filters: dict[TBookListField, int | str | bool] = {}
    ) -> list[Book]:
        _id = int(filters.get("id", 0))
        _isbn = str(filters.get("isbn", ""))
        _titre = str(filters.get("titre", ""))
        _numero = int(filters.get("numero", 0))
        try:
            query = Query()
            items = self.__store.search(
                (query.id == _id if _id else query.id.exists())
                & (query.isbn == _isbn if _isbn else query.isbn.exists())
                & (query.titre == _titre if _titre else query.titre.exists())
                & (query.numero == _numero if _numero else query.numero.exists())
            )
            self.__logger.info(
                f"Listed {len(items)} books from TinyDB",
            )
            data = self.__to_entities(items)
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
            data = cast(Document | None, self.__store.get(doc_id=id))
            if not data:
                return None

            item = self.__to_entity(data)
            item.prices = await self.__prices.list({"isbn": item.isbn})

            return item
        except Exception as e:
            self.__logger.error(
                f"Error getting book for id '{id}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def upsert_many(self, entities: list[Book]) -> list[Book]:
        results: list[Book] = []
        for entity in entities:
            item = await self.upsert(entity)
            if item:
                results.append(item)

        return results

    async def upsert(self, entity: Book) -> Book | None:
        try:
            item = copy.deepcopy(entity)
            prices_to_store: list[BookPrice] = item.prices
            item.prices = []

            await self.__prices.upsert_many(prices_to_store)

            document = self.__to_document(item)
            id = self.__store.upsert(
                document,
                (Query().id == entity.id),
            )
            if not id:
                self.__logger.warning(
                    f"Failed to upsert book n°'{entity.numero}' (id: {entity.id}) in TinyDB"
                )
                return None

            item = await self.get(id[0])
            if not item:
                self.__logger.warning(
                    f"Failed to retrieve upserted book n°'{entity.numero}' (id: {entity.id}) in TinyDB"
                )
                return None

            return item
        except Exception as e:
            self.__logger.error(
                f"Error upserting book n°'{entity.numero}' (id: {entity.id}): {type(e).__name__}: {e}",
                exc_info=True,
            )

        return None
