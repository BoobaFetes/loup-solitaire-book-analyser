import copy
import logging

from domain import Book, BookPrice
from ports.database import IUnitOfWork
from usecases.price.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class BookPriceUseCases:
    """Use cases for managing books."""

    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        sources: list[PriceSourceUsecasesBase],
    ):
        self.__unit_of_work = unit_of_work
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__sources: list[PriceSourceUsecasesBase] = sources

    def __should_store(
        self,
        price: BookPrice,
        last_prices_by_source: dict[str, dict[str, BookPrice | None]],
    ) -> bool:
        """
        we need to add to the store if (or conditions):
        1. there is no stored price
        2. price has changed (if prices are equals, the stored prices willl not be updated)
        """
        if price.currency == "not set":
            return False

        stored_price = last_prices_by_source.get(price.isbn, {}).get(price.source)

        return not stored_price or (
            price != stored_price and price.price != stored_price.price
        )

    async def fetch_prices(self, books: list[Book]) -> dict[str, list[BookPrice]]:
        results: dict[str, list[BookPrice]] = {}
        prices_to_store: list[BookPrice] = []

        last_prices_by_source = (
            await self.__unit_of_work.prices.dict_last_price_of_source_by_isbns(
                sources=[source.base_url for source in self.__sources],
                isbns=[book.isbn for book in books],
            )
        )

        for source in self.__sources:
            self.__logger.info(f"Fetching prices from {source.base_url}")
            prices = await source.fetch_bookprices(books)
            for item in prices:
                # on peut avoir les isbns depuis les Book mais le fait de le recupérer depuis un price permet de s'assurer de la cohérence entre le livre et son prix, depuis deux source distinctes
                results.setdefault(item.isbn, []).append(item)
                # add to store list only it should be
                if self.__should_store(item, last_prices_by_source):
                    prices_to_store.append(item)

        stored_items = await self.__unit_of_work.prices.upsert_many(prices_to_store)
        self.__logger.info(
            f"Added {len(stored_items)} prices for {len(prices_to_store)} books from {len(self.__sources)} sources"
        )

        return results

    async def bind_prices_to_books(self, books: list[Book]) -> list[Book]:
        data = copy.deepcopy(books)
        prices_by_isbn = await self.__unit_of_work.prices.dict_by_isbns(
            [book.isbn for book in books]
        )

        for book in data:
            book.prices = prices_by_isbn.get(book.isbn, [])

        return data
