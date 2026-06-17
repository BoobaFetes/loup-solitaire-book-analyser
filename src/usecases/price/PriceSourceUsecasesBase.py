import logging
from abc import ABC, abstractmethod

from domain import Book, BookPrice


class PriceSourceUsecasesBase(ABC):
    def __init__(
        self,
        base_url: str,
        parallel_calls: int = 5,
    ):
        self.base_url = base_url
        self._logger = logging.getLogger(self.__class__.__name__)
        self._parallel_calls = parallel_calls

    @abstractmethod
    async def fetch_bookprices(self, books: list[Book]) -> list[BookPrice]: ...

    @abstractmethod
    async def fetch_bookprice(self, book: Book, **kwargs) -> BookPrice | None: ...
