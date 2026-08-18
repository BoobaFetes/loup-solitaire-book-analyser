import logging
from datetime import date

from adapters.database.sqlalchemy.DbContext import DbContext
from domain import BookPrice
from ports.database import IBookPriceRepository, TBookPriceListField
from persistence.sqlalchemy.entities.BookPriceEntity import BookPriceEntity
from sqlalchemy import Select, select


class BookPriceRepository(IBookPriceRepository):
    """Implémentation d'un dépôt de book prices basé sur SQLAlchemy.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookPriceRepositoryInterface (BookPriceRepositoryInterface): Interface du dépôt de book prices.
    """

    def __init__(self, context: DbContext):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__context = context

    def __to_entities_as_dict(
        self, data: list[BookPriceEntity]
    ) -> dict[str, list[BookPrice]]:
        result: dict[str, list[BookPrice]] = {}
        for item in data:
            entity = self.__to_entity(item)
            result.setdefault(entity.isbn, []).append(entity)
        return result

    def __to_entities(self, data: list[BookPriceEntity]) -> list[BookPrice]:
        return [self.__to_entity(item) for item in data]

    def __to_entity(self, data: BookPriceEntity) -> BookPrice:
        return BookPrice(
            isbn=data.isbn,
            source=data.source,
            date=data.date,
            price=data.price,
            url=data.url,
            currency=data.currency,
        )

    def __to_orm_entity(self, entity: BookPrice) -> BookPriceEntity:
        return BookPriceEntity(
            isbn=entity.isbn,
            source=entity.source,
            date=entity.date,
            price=entity.price,
            url=entity.url,
            currency=entity.currency,
        )

    def __select(self) -> Select[tuple[BookPriceEntity]]:
        return select(BookPriceEntity).order_by(
            BookPriceEntity.isbn,
            BookPriceEntity.source,
            BookPriceEntity.date,
        )

    async def dict_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        try:
            statement = self.__select()
            if isbns:
                statement = statement.where(BookPriceEntity.isbn.in_(isbns))

            with self.__context.operation_session() as session:
                data = list(session.scalars(statement))
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
            statement = self.__select().where(BookPriceEntity.source.in_(sources))
            if isbns:
                statement = statement.where(BookPriceEntity.isbn.in_(isbns))

            with self.__context.operation_session() as session:
                data = list(session.scalars(statement))

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
            statement = self.__select()
            if _isbn:
                statement = statement.where(BookPriceEntity.isbn == _isbn)
            if _source:
                statement = statement.where(BookPriceEntity.source == _source)
            if _date:
                statement = statement.where(BookPriceEntity.date == date.fromisoformat(_date))

            with self.__context.operation_session() as session:
                data = self.__to_entities(list(session.scalars(statement)))

            self.__logger.info(
                f"Listed {len(data)} book prices for ISBN='{_isbn}' and source='{_source}' and date='{_date}' from SQLAlchemy",
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
            with self.__context.operation_session() as session:
                data = session.get(
                    BookPriceEntity,
                    {
                        "isbn": _isbn,
                        "source": _source,
                        "date": _date,
                    },
                )
            if data is None:
                self.__logger.info(
                    f"No book price found for ISBN '{_isbn}' and source '{_source}' and date '{_date}' in SQLAlchemy"
                )
                return None
            return self.__to_entity(data)
        except Exception as e:
            self.__logger.error(
                f"Error getting book price for ISBN '{_isbn}' and source '{_source}' and date '{_date}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def add_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        results: list[BookPrice] = []
        for entity in entities:
            item = await self.add(entity)
            if item:
                results.append(item)

        return results

    async def add(self, entity: BookPrice) -> BookPrice | None:
        try:
            with self.__context.operation_session() as session:
                session.add(self.__to_orm_entity(entity))
                session.flush()
                item = session.get(
                    BookPriceEntity,
                    {
                        "isbn": entity.isbn,
                        "source": entity.source,
                        "date": entity.date,
                    },
                )
                return self.__to_entity(item) if item else None
        except Exception as e:
            self.__logger.error(
                f"Error adding book price for ISBN '{entity.isbn}' and source '{entity.source}' on date '{entity.date.isoformat()}': {type(e).__name__}: {e}",
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
            with self.__context.operation_session() as session:
                item = session.merge(self.__to_orm_entity(entity))
                session.flush()
                return self.__to_entity(item)
        except Exception as e:
            self.__logger.error(
                f"Error upserting book price for ISBN '{entity.isbn}' and source '{entity.source}' on date '{entity.date.isoformat()}': {type(e).__name__}: {e}",
                exc_info=True,
            )

        return None

    async def update_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        results: list[BookPrice] = []
        for entity in entities:
            item = await self.update(entity)
            if item:
                results.append(item)

        return results

    async def update(self, entity: BookPrice) -> BookPrice | None:
        try:
            with self.__context.operation_session() as session:
                item = session.get(
                    BookPriceEntity,
                    {
                        "isbn": entity.isbn,
                        "source": entity.source,
                        "date": entity.date,
                    },
                )
                if item is None:
                    return None
                item.price = entity.price
                item.url = entity.url
                item.currency = entity.currency
                session.flush()
                return self.__to_entity(item)
        except Exception as e:
            self.__logger.error(
                f"Error updating book price for ISBN '{entity.isbn}' and source '{entity.source}' on date '{entity.date.isoformat()}': {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None
