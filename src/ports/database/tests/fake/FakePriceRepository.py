from datetime import date

from domain import BookPrice
from ports.database import IBookPriceRepository, TBookPriceListField


class FakePriceRepository(IBookPriceRepository):
    def __init__(self) -> None:
        self.upserted: list[BookPrice] = []

    async def dict_last_price_of_source_by_isbns(
        self,
        sources: list[str],
        isbns: list[str] = [],
    ) -> dict[str, dict[str, BookPrice | None]]:
        raise NotImplementedError

    async def dict_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        raise NotImplementedError

    async def list(
        self, filters: dict[TBookPriceListField, int | str | bool] = {}
    ) -> list[BookPrice]:
        raise NotImplementedError

    async def get(self, id: tuple[str, str, date]) -> BookPrice | None:
        raise NotImplementedError

    async def upsert_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        self.upserted.extend(entities)
        return entities

    async def upsert(self, entity: BookPrice) -> BookPrice | None:
        raise NotImplementedError

    async def add_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        raise NotImplementedError

    async def add(self, entity: BookPrice) -> BookPrice | None:
        raise NotImplementedError

    async def update_many(self, entities: list[BookPrice]) -> list[BookPrice]:
        raise NotImplementedError

    async def update(self, entity: BookPrice) -> BookPrice | None:
        raise NotImplementedError
