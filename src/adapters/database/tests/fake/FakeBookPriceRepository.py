from domain import BookPrice
from ports.database import IBookPriceRepository, TBookPriceListField
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeBookPriceRepository(IBookPriceRepository[tuple[str, str]], SpyStubFake):
    def __init__(
        self,
        last_prices: dict[str, dict[str, BookPrice | None]] | None = None,
        prices_by_isbn: dict[str, list[BookPrice]] | None = None,
    ) -> None:
        SpyStubFake.__init__(self)
        self.last_prices = last_prices or {}
        self.prices_by_isbn = prices_by_isbn or {}
        self.upserted_items: list[BookPrice] = []
        self.added_items: list[BookPrice] = []
        self.updated_items: list[BookPrice] = []

    def stub_list(self, returned: list[BookPrice]) -> None:
        self._stub("list", returned)

    @property
    def spy_list(self) -> list[SpyCall]:
        return self._spy("list")

    def stub_get(self, returned: BookPrice | None) -> None:
        self._stub("get", returned)

    @property
    def spy_get(self) -> list[SpyCall]:
        return self._spy("get")

    def stub_upsert_many(self, returned: list[BookPrice]) -> None:
        self._stub("upsert_many", returned)

    @property
    def spy_upsert_many(self) -> list[SpyCall]:
        return self._spy("upsert_many")

    def stub_upsert(self, returned: BookPrice | None) -> None:
        self._stub("upsert", returned)

    @property
    def spy_upsert(self) -> list[SpyCall]:
        return self._spy("upsert")

    def stub_add_many(self, returned: list[BookPrice]) -> None:
        self._stub("add_many", returned)

    @property
    def spy_add_many(self) -> list[SpyCall]:
        return self._spy("add_many")

    def stub_add(self, returned: BookPrice | None) -> None:
        self._stub("add", returned)

    @property
    def spy_add(self) -> list[SpyCall]:
        return self._spy("add")

    def stub_update_many(self, returned: list[BookPrice]) -> None:
        self._stub("update_many", returned)

    @property
    def spy_update_many(self) -> list[SpyCall]:
        return self._spy("update_many")

    def stub_update(self, returned: BookPrice | None) -> None:
        self._stub("update", returned)

    @property
    def spy_update(self) -> list[SpyCall]:
        return self._spy("update")

    def stub_dict_last_price_of_source_by_isbns(
        self, returned: dict[str, dict[str, BookPrice | None]]
    ) -> None:
        self._stub("dict_last_price_of_source_by_isbns", returned)

    @property
    def spy_dict_last_price_of_source_by_isbns(self) -> list[SpyCall]:
        return self._spy("dict_last_price_of_source_by_isbns")

    def stub_dict_by_isbns(self, returned: dict[str, list[BookPrice]]) -> None:
        self._stub("dict_by_isbns", returned)

    @property
    def spy_dict_by_isbns(self) -> list[SpyCall]:
        return self._spy("dict_by_isbns")

    async def list(
        self, filters: dict[TBookPriceListField, int | str | bool] = {}
    ) -> list[BookPrice]:
        returned = self._returned_or_default("list", [])
        return self._record_call("list", (), {"filters": filters}, returned)

    async def get(self, id: tuple[str, str]) -> BookPrice | None:
        returned = self._returned_or_default("get", None)
        return self._record_call("get", (id,), {}, returned)

    async def upsert_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        self.upserted_items.extend(entities)
        returned = self._returned_or_default("upsert_many", list(entities))
        return self._record_call("upsert_many", (entities,), {}, returned)

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        self.upserted_items.append(entity)
        returned = self._returned_or_default("upsert", entity)
        return self._record_call("upsert", (entity,), {}, returned)

    async def add_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        self.added_items.extend(entities)
        returned = self._returned_or_default("add_many", entities)
        return self._record_call("add_many", (entities,), {}, returned)

    async def add(self, entity: BookPrice) -> BookPrice | None:
        self.added_items.append(entity)
        returned = self._returned_or_default("add", entity)
        return self._record_call("add", (entity,), {}, returned)

    async def update_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        self.updated_items.extend(entities)
        returned = self._returned_or_default("update_many", entities)
        return self._record_call("update_many", (entities,), {}, returned)

    async def update(self, entity: BookPrice) -> BookPrice | None:
        self.updated_items.append(entity)
        returned = self._returned_or_default("update", entity)
        return self._record_call("update", (entity,), {}, returned)

    async def dict_last_price_of_source_by_isbns(
        self, sources: list[str], isbns: list[str] = []
    ) -> dict[str, dict[str, BookPrice | None]]:
        returned = self._returned_or_default(
            "dict_last_price_of_source_by_isbns", self.last_prices
        )
        return self._record_call(
            "dict_last_price_of_source_by_isbns",
            (sources,),
            {"isbns": isbns},
            returned,
        )

    async def dict_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        returned = self._returned_or_default("dict_by_isbns", self.prices_by_isbn)
        return self._record_call("dict_by_isbns", (), {"isbns": isbns}, returned)
