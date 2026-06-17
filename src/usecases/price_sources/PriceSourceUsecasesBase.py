import logging

from domain import Book, BookPrice
from ports import BrowserInterface, BrowserTypes


class PriceSourceUsecasesBase:
    def __init__(
        self,
        url_base: str,
        parallel_calls: int = 5,
    ):
        self.url_base = url_base
        self._logger = logging.getLogger(self.__class__.__name__)
        self._parallel_calls = parallel_calls

    def _build_search_url_by_isbn(self, isbn: str) -> str:
        raise NotImplementedError(
            "_build_search_url_by_isbn method must be implemented by subclasses"
        )

    async def fetch_bookprices(
        self,
        books: list[Book],
        browser: BrowserInterface[
            BrowserTypes.TBrowser, BrowserTypes.TPage, BrowserTypes.TElement
        ],
        context_index: int = 0,
    ) -> list[BookPrice]:
        raise NotImplementedError(
            "fetch_bookprices method must be implemented by subclasses"
        )

    async def fetch_bookprice(
        self,
        book: Book,
        browser: BrowserInterface[
            BrowserTypes.TBrowser, BrowserTypes.TPage, BrowserTypes.TElement
        ],
    ) -> BookPrice | None:
        raise NotImplementedError(
            "fetch_bookprice method must be implemented by subclasses"
        )
