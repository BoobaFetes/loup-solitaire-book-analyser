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
        prices_to_store: list[BookPrice] = []

        last_prices_by_source = self._repository.list_last_price_of_source_by_isbns(
            [source.url_base for source in self._sources], [book.isbn for book in books]
        )

        def should_store(price: BookPrice) -> bool:
            # on veut stocker le prix si c'est une mise à jour (prix différent ou même prix mais date différente) ou si c'est un nouveau prix
            # if there is not price yet => add it
            stored_price = last_prices_by_source.get(price.isbn, {}).get(price.source)

            if not stored_price:
                return True

            # if prices or dates are different => add it
            return price.date != stored_price.date or price.price != stored_price.price

        async with self._browser as browser:
            for source in self._sources:
                browser_context_index = await browser.new_context()
                self._logger.info(f"Fetching prices from {source.url_base}")
                prices = await source.fetch_bookprices(
                    books, browser, browser_context_index
                )

                # on peut avoir les isbns depuis les Book mais le fait de le recupérer depuis le prices permet de s'assurer qu'ils sont bien transmis au BookPrice
                for item in prices:
                    # add to results for return to compare with the database
                    # with this results, the team can check the database and see if new prices is well stored
                    if not results.get(item.isbn):
                        results[item.isbn] = []
                    results[item.isbn].append(item)

                    # add to store list only it should be
                    if should_store(item):
                        prices_to_store.append(item)

        added_items_count = self._repository.add_many(prices_to_store)
        self._logger.info(
            f"Added {added_items_count} prices for {len(prices_to_store)} books from {len(self._sources)} sources"
        )

        return results

    async def bind_prices_to_books(self, books: list[Book]) -> list[Book]:
        data = copy.deepcopy(books)
        prices_by_isbn = self._repository.list_by_isbns([book.isbn for book in books])

        for book in data:
            book.prices = prices_by_isbn.get(book.isbn, [])

        return data
