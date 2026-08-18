import logging
from datetime import date

from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from adapters.database.sqlalchemy.DbContext import DbContext
from domain import Book, BookPrice
from ports.database import IBookRepository, TBookListField
from persistence.sqlalchemy.entities.AuthorEntity import AuthorEntity
from persistence.sqlalchemy.entities.BookAuthorEntity import BookAuthorEntity
from persistence.sqlalchemy.entities.BookEntity import BookEntity
from persistence.sqlalchemy.entities.BookPriceEntity import BookPriceEntity


class BookRepository(IBookRepository):
    def __init__(self, context: DbContext):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__context = context

    def __select(self) -> Select[tuple[BookEntity]]:
        return (
            select(BookEntity)
            .options(
                joinedload(BookEntity.authors).joinedload(BookAuthorEntity.author),
                joinedload(BookEntity.prices),
            )
            .order_by(BookEntity.id)
        )

    def __to_entity(self, data: BookEntity) -> Book:
        authors = [
            book_author.author.name
            for book_author in sorted(data.authors, key=lambda item: item.position)
        ]
        return Book(
            id=data.id,
            url=data.url,
            isbn=data.isbn,
            numero=data.numero,
            titre=data.titre,
            authors=authors,
            lastParutionDate=data.lastParutionDate,
            description=data.description,
            official=data.official,
            image=data.image,
            acquired=data.acquired,
            prices=[
                BookPrice(
                    isbn=price.isbn,
                    source=price.source,
                    date=price.date,
                    price=price.price,
                    url=price.url,
                    currency=price.currency,
                )
                for price in sorted(
                    data.prices,
                    key=lambda item: (item.source, item.date),
                )
            ],
        )

    def __copy_to_orm(self, source: Book, target: BookEntity) -> None:
        target.id = source.id
        target.url = source.url
        target.isbn = source.isbn
        target.numero = source.numero
        target.titre = source.titre
        target.lastParutionDate = self.__to_date(source.lastParutionDate)
        target.description = source.description
        target.official = source.official
        target.image = source.image
        target.acquired = source.acquired

    def __to_date(self, value: date | str) -> date:
        if isinstance(value, date):
            return value
        return date.fromisoformat(value)

    async def list(
        self, filters: dict[TBookListField, int | str | bool] = {}
    ) -> list[Book]:
        _id = int(filters.get("id", 0))
        _isbn = str(filters.get("isbn", ""))
        _titre = str(filters.get("titre", ""))
        _numero = int(filters.get("numero", 0))
        try:
            statement = self.__select()
            if _id:
                statement = statement.where(BookEntity.id == _id)
            if _isbn:
                statement = statement.where(BookEntity.isbn == _isbn)
            if _titre:
                statement = statement.where(BookEntity.titre == _titre)
            if _numero:
                statement = statement.where(BookEntity.numero == _numero)

            with self.__context.operation_session() as session:
                items = list(session.scalars(statement).unique())
                data = [self.__to_entity(item) for item in items]
            self.__logger.info("Listed %s books from SQLAlchemy", len(data))
            return data
        except Exception as e:
            self.__logger.error(
                f"Error listing books: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return []

    async def get(self, id: int) -> Book | None:
        try:
            statement = self.__select().where(BookEntity.id == id)
            with self.__context.operation_session() as session:
                item = session.scalars(statement).unique().one_or_none()
                return self.__to_entity(item) if item else None
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
            with self.__context.operation_session() as session:
                item = session.get(BookEntity, entity.id)
                if item is None:
                    item = session.scalar(
                        select(BookEntity).where(BookEntity.isbn == entity.isbn)
                    )
                if item is None:
                    item = BookEntity()
                    session.add(item)

                self.__copy_to_orm(entity, item)
                item.authors.clear()

                for position, author_name in enumerate(entity.authors):
                    author = session.scalar(
                        select(AuthorEntity).where(AuthorEntity.name == author_name)
                    )
                    if author is None:
                        author = AuthorEntity(name=author_name)
                    item.authors.append(
                        BookAuthorEntity(author=author, position=position)
                    )

                session.flush()
                for price in entity.prices:
                    session.merge(
                        BookPriceEntity(
                            isbn=price.isbn,
                            source=price.source,
                            date=price.date,
                            price=price.price,
                            url=price.url,
                            currency=price.currency,
                        )
                    )
                session.flush()
                return self.__to_entity(item)
        except Exception as e:
            self.__logger.error(
                f"Error upserting book n°'{entity.numero}' (id: {entity.id}): {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def add_many(self, entities: list[Book]) -> list[Book]:
        results: list[Book] = []
        for entity in entities:
            item = await self.add(entity)
            if item:
                results.append(item)
        return results

    async def add(self, entity: Book) -> Book | None:
        try:
            with self.__context.operation_session() as session:
                item = BookEntity()
                self.__copy_to_orm(entity, item)
                session.add(item)
                session.flush()
                return self.__to_entity(item)
        except Exception as e:
            self.__logger.error(
                f"Error adding book n°'{entity.numero}' (id: {entity.id}): {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    async def update_many(self, entities: list[Book]) -> list[Book]:
        results: list[Book] = []
        for entity in entities:
            item = await self.update(entity)
            if item:
                results.append(item)
        return results

    async def update(self, entity: Book) -> Book | None:
        try:
            with self.__context.operation_session() as session:
                item = session.get(BookEntity, entity.id)
                if item is None:
                    return None
                self.__copy_to_orm(entity, item)
                session.flush()
                return self.__to_entity(item)
        except Exception as e:
            self.__logger.error(
                f"Error updating book n°'{entity.numero}' (id: {entity.id}): {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None
