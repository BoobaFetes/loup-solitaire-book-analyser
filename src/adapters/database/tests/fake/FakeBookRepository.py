from domain import Book
from ports.database import IBookRepository, TBookListField
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeBookRepository(IBookRepository[int], SpyStubFake):
    def __init__(self, items: list[Book] | None = None) -> None:
        SpyStubFake.__init__(self)
        self.items = list(items or [])
        self.upserted_items: list[Book] = []
        self.added_items: list[Book] = []
        self.updated_items: list[Book] = []

    def stub_list(self, returned: list[Book]) -> None:
        self._stub("list", returned)

    @property
    def spy_list(self) -> list[SpyCall]:
        return self._spy("list")

    def stub_get(self, returned: Book | None) -> None:
        self._stub("get", returned)

    @property
    def spy_get(self) -> list[SpyCall]:
        return self._spy("get")

    def stub_upsert_many(self, returned: list[Book]) -> None:
        self._stub("upsert_many", returned)

    @property
    def spy_upsert_many(self) -> list[SpyCall]:
        return self._spy("upsert_many")

    def stub_upsert(self, returned: Book | None) -> None:
        self._stub("upsert", returned)

    @property
    def spy_upsert(self) -> list[SpyCall]:
        return self._spy("upsert")

    def stub_add_many(self, returned: list[Book]) -> None:
        self._stub("add_many", returned)

    @property
    def spy_add_many(self) -> list[SpyCall]:
        return self._spy("add_many")

    def stub_add(self, returned: Book | None) -> None:
        self._stub("add", returned)

    @property
    def spy_add(self) -> list[SpyCall]:
        return self._spy("add")

    def stub_update_many(self, returned: list[Book]) -> None:
        self._stub("update_many", returned)

    @property
    def spy_update_many(self) -> list[SpyCall]:
        return self._spy("update_many")

    def stub_update(self, returned: Book | None) -> None:
        self._stub("update", returned)

    @property
    def spy_update(self) -> list[SpyCall]:
        return self._spy("update")

    async def list(
        self, filters: dict[TBookListField, int | str | bool] = {}
    ) -> list[Book]:
        returned = self._returned_or_default("list", list(self.items))
        return self._record_call("list", (), {"filters": filters}, returned)

    async def get(self, id: int) -> Book | None:
        default = next((book for book in self.items if book.id == id), None)
        returned = self._returned_or_default("get", default)
        return self._record_call("get", (id,), {}, returned)

    async def upsert_many(self, entities: list[Book]) -> list[Book]:
        self.upserted_items = list(entities)
        self.items = list(entities)
        returned = self._returned_or_default("upsert_many", list(entities))
        return self._record_call("upsert_many", (entities,), {}, returned)

    async def upsert(self, entity: Book) -> Book | None:
        self.upserted_items.append(entity)
        self.items.append(entity)
        returned = self._returned_or_default("upsert", entity)
        return self._record_call("upsert", (entity,), {}, returned)

    async def add_many(self, entities: list[Book]) -> list[Book]:
        self.added_items.extend(entities)
        self.items.extend(entities)
        returned = self._returned_or_default("add_many", entities)
        return self._record_call("add_many", (entities,), {}, returned)

    async def add(self, entity: Book) -> Book | None:
        self.added_items.append(entity)
        self.items.append(entity)
        returned = self._returned_or_default("add", entity)
        return self._record_call("add", (entity,), {}, returned)

    async def update_many(self, entities: list[Book]) -> list[Book]:
        self.updated_items.extend(entities)
        self.items.extend(entities)
        returned = self._returned_or_default("update_many", entities)
        return self._record_call("update_many", (entities,), {}, returned)

    async def update(self, entity: Book) -> Book | None:
        self.updated_items.append(entity)
        self.items.append(entity)
        returned = self._returned_or_default("update", entity)
        return self._record_call("update", (entity,), {}, returned)
