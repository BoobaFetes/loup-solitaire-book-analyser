from domain import BookPrice
from ports.database import IBookPriceRepository, TBookPriceListField


class FakeBookPriceRepository(IBookPriceRepository[tuple[str, str]]):
    def __init__(
        self,
        last_prices: dict[str, dict[str, BookPrice | None]] | None = None,
        prices_by_isbn: dict[str, list[BookPrice]] | None = None,
    ) -> None:
        self.last_prices = last_prices or {}
        self.prices_by_isbn = prices_by_isbn or {}
        self.upserted_items: list[BookPrice] = []

    async def list(
        self, filters: dict[TBookPriceListField, int | str | bool] = {}
    ) -> list[BookPrice]:
        return []

    async def get(self, id: tuple[str, str]) -> BookPrice | None:
        return None

    async def upsert_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        self.upserted_items = list(entities)
        return list(entities)

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        return entity

    async def add_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        return entities

    async def add(self, entity: BookPrice) -> BookPrice | None:
        return entity

    async def update_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        return entities

    async def update(self, entity: BookPrice) -> BookPrice | None:
        return entity

    async def dict_last_price_of_source_by_isbns(
        self, sources: list[str], isbns: list[str] = []
    ) -> dict[str, dict[str, BookPrice | None]]:
        return self.last_prices

    async def dict_by_isbns(
        self, isbns: list[str] = []
    ) -> dict[str, list[BookPrice]]:
        return self.prices_by_isbn
