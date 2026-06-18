import asyncio
from collections.abc import Callable
from typing import cast

from domain import Book, BookPrice
from ports.http import HttpClientBase
from ports.usecase import PriceDetailsFinderBase
from usecases.price.PriceSourceUsecasesBase import PriceSourceUsecasesBase
from usecases.UnitTestCapture import UnitTestCapture


class GallimardPriceSourceUsecases(PriceSourceUsecasesBase):
    def __init__(
        self,
        client: HttpClientBase,
        base_url: str,
        details_factory: Callable[[str], PriceDetailsFinderBase],
        parallel_calls: int = 5,
    ):
        super().__init__(base_url, parallel_calls)
        self.__client = client
        self.__details_factory = details_factory

    async def fetch_bookprices(self, books: list[Book]) -> list[BookPrice]:
        results: list[BookPrice] = []
        self._logger.info(f"searching book prices for {len(books)} books")

        async with self.__client as client_instance:
            for i in range(0, len(books), self._parallel_calls):
                selected_books = books[i : i + self._parallel_calls]
                prices = await asyncio.gather(
                    *[
                        self.fetch_bookprice(book, client=client_instance)
                        for book in selected_books
                    ]
                )
                results.extend([price for price in prices if price])

        return results

    async def fetch_bookprice(self, book: Book, **kwargs) -> BookPrice | None:
        # check parameters
        client = cast(HttpClientBase | None, kwargs.get("client", None))
        if client and not isinstance(client, HttpClientBase):
            raise ValueError("client must be an instance of HttpClientBase or None")

        # action
        try:
            active_client = client or self.__client
            html = await active_client.get_text(book.url)
            if not html:
                self._logger.warning(
                    f"No HTML content retrieved for book URL {book.url}"
                )
                return None

            finders = self.__details_factory(html)
            (price, currency) = finders.price_and_currency()

            UnitTestCapture.capture(
                f"src/usecases/price/tests/dataset/gallimard_{book.isbn}.html", html
            )
            return BookPrice(
                isbn=book.isbn,
                source=self.base_url,
                price=price,
                currency=currency,
                url=book.url,
            )
        except Exception as e:
            self._logger.error(
                f"Error while fetching book details for {book.url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )
            return None
