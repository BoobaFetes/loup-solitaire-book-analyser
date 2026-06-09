import copy
import logging

from adapters import BookPriceFileRepository
from adapters.BrowserHandlers.types import TBrowser, TElement, TPage
from domain import Book, BookPrice
from ports import BrowserInterface
from usecases.price_sources import PriceSourceUsecasesBase


class BookPriceUseCases:
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        repository: BookPriceFileRepository,
        browser: BrowserInterface[TBrowser, TPage, TElement],
        sources: list[PriceSourceUsecasesBase],
    ):
        self._repository = repository
        self._browser = browser
        self._logger = logging.getLogger(self.__class__.__name__)
        self._sources: list[PriceSourceUsecasesBase] = sources

    async def fetch_prices(self, books: list[Book]) -> dict[str, list[BookPrice]]:
        results: dict[str, list[BookPrice]] = {}

        async with self._browser as browser:
            for source in self._sources:
                browser_context_index = await browser.new_context()
                self._logger.info(f"Fetching prices from {source.url_base}")
                prices = await source.fetch_bookprices(
                    books, browser, browser_context_index
                )

                for k, v in [(p.isbn, p) for p in prices]:
                    if not results.get(k):
                        results[k] = [v]
                    else:
                        results[k].append(v)

        added_items_count = self._repository.add_many(
            [price for prices in results.values() for price in prices]
        )
        self._logger.info(
            f"Added {added_items_count} prices for {len(books)} books from {len(self._sources)} sources"
        )

        return results

    async def bind_prices_to_books(self, books: list[Book]) -> list[Book]:
        data = copy.deepcopy(books)
        prices_by_isbn = self._repository.list_by_isbns([book.isbn for book in books])

        for book in data:
            book.prices = prices_by_isbn.get(book.isbn, [])

        return data
