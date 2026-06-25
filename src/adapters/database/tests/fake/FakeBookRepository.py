from domain import Book
from ports.database import IBookRepository, TBookListField


class FakeBookRepository(IBookRepository[int]):
    def __init__(self, items: list[Book] | None = None) -> None:
        self.items = list(items or [])
        self.upserted_items: list[Book] = []
        self.added_items: list[Book] = []
        self.updated_items: list[Book] = []

    async def list(
        self, filters: dict[TBookListField, int | str | bool] = {}
    ) -> list[Book]:
        return list(self.items)

    async def get(self, id: int) -> Book | None:
        return next((book for book in self.items if book.id == id), None)

    async def upsert_many(self, entities: list[Book]) -> list[Book]:
        self.upserted_items = list(entities)
        self.items = list(entities)
        return list(entities)

    async def upsert(self, entity: Book) -> Book | None:
        self.upserted_items.append(entity)
        self.items.append(entity)
        return entity

    async def add_many(self, entities: list[Book]) -> list[Book]:
        self.added_items.extend(entities)
        self.items.extend(entities)
        return entities

    async def add(self, entity: Book) -> Book | None:
        self.added_items.append(entity)
        self.items.append(entity)
        return entity

    async def update_many(self, entities: list[Book]) -> list[Book]:
        self.updated_items.extend(entities)
        self.items.extend(entities)
        return entities

    async def update(self, entity: Book) -> Book | None:
        self.updated_items.append(entity)
        self.items.append(entity)
        return entity
