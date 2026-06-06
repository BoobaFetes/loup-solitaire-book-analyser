import logging

from adapters.BrowserHandlers.types import TBrowser, TElement, TPage
from domain import BookPrice
from ports import BookRepositoryInterface
from ports.BrowserInterface import BrowserInterface


class PriceSourceUsecasesBase:
    def __init__(
        self,
        repository: BookRepositoryInterface,
        url_base: str,
        parallel_calls: int = 5,
    ):
        self.url_base = url_base
        self._repository = repository
        self._logger = logging.getLogger(self.__class__.__name__)
        self._parallel_calls = parallel_calls

    def _build_search_url_by_isbn(self, isbn: str) -> str:
        raise NotImplementedError(
            "_build_search_url_by_isbn method must be implemented by subclasses"
        )

    async def fetch_bookprices(
        self, isbns: list[str], browser: BrowserInterface[TBrowser, TPage, TElement]
    ) -> list[BookPrice]:
        raise NotImplementedError(
            "fetch_bookprices method must be implemented by subclasses"
        )

    async def fetch_bookprice(
        self, isbn: str, browser: BrowserInterface[TBrowser, TPage, TElement]
    ) -> BookPrice | None:
        raise NotImplementedError(
            "fetch_bookprice method must be implemented by subclasses"
        )
