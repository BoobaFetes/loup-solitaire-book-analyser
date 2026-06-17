import copy
import logging

from adapters.browser.types import TBrowser, TElement, TPage
from domain import Book, BookPrice
from ports import BrowserInterface, IUnitOfWork
from usecases.price_sources import PriceSourceUsecasesBase


class BookPriceUseCases:
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        browser: BrowserInterface[TBrowser, TPage, TElement],
        sources: list[PriceSourceUsecasesBase],
    ):
        self._unit_of_work = unit_of_work
        self._browser = browser
        self._logger = logging.getLogger(self.__class__.__name__)
        self._sources: list[PriceSourceUsecasesBase] = sources

    async def fetch_prices(self, books: list[Book]) -> dict[str, list[BookPrice]]:
        results: dict[str, list[BookPrice]] = {}
        prices_to_store: list[BookPrice] = []

        last_prices_by_source = (
            await self._unit_of_work.prices.dict_last_price_of_source_by_isbns(
                sources=[source.url_base for source in self._sources],
                isbns=[book.isbn for book in books],
            )
        )

        def should_store(price: BookPrice) -> bool:
            """
            we need to add to the store if (or conditions):
            1. there is no stored price
            2. price has changed (if prices are equals, the stored prices willl not be updated)
            """
            stored_price = last_prices_by_source.get(price.isbn, {}).get(price.source)

            return not stored_price or (
                price != stored_price and price.price != stored_price.price
            )

        async with self._browser as browser:
            for source in self._sources:
                browser_context_index = await browser.new_context()
                self._logger.info(f"Fetching prices from {source.url_base}")
                prices = await source.fetch_bookprices(
                    books, browser, browser_context_index
                )

                # on peut avoir les isbns depuis les Book mais le fait de le recupérer depuis le prices permet de s'assurer qu'ils sont bien transmis au BookPrice
                for item in prices:
                    results.setdefault(item.isbn, []).append(item)
                    # add to store list only it should be
                    if should_store(item):
                        prices_to_store.append(item)

        stored_items = await self._unit_of_work.prices.upsert_many(prices_to_store)
        self._logger.info(
            f"Added {len(stored_items)} prices for {len(prices_to_store)} books from {len(self._sources)} sources"
        )

        return results

    async def bind_prices_to_books(self, books: list[Book]) -> list[Book]:
        data = copy.deepcopy(books)
        prices_by_isbn = await self._unit_of_work.prices.dict_by_isbns(
            [book.isbn for book in books]
        )

        for book in data:
            book.prices = prices_by_isbn.get(book.isbn, [])

        return data
