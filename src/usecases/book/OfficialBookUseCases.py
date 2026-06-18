import asyncio
import logging
from collections.abc import Callable
from typing import Literal

from domain import Book, BookPrice
from ports.http import HttpClientBase
from ports.usecase import (
    BookDetailsFinderBase,
    BookListFinderBase,
    PriceDetailsFinderBase,
)
from usecases.UnitTestCapture import UnitTestCapture


class OfficialBookUseCases:
    """Use cases for managing books."""

    def __init__(
        self,
        base_url: str,
        client: HttpClientBase,
        list_factory: Callable[[str], BookListFinderBase],
        details_factory: Callable[[str], BookDetailsFinderBase],
        price_details_factory: Callable[[str], PriceDetailsFinderBase],
        parallel_calls: int = 5,
    ):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__client = client
        self.__base_url = base_url
        self.__list_factory = list_factory
        self.__details_factory = details_factory
        self.__price_details_factory = price_details_factory
        self.__parallel_calls = parallel_calls

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        results: list[Book] = []

        active_client = client or self.__client
        async with active_client as client_instance:
            self.__logger.info(f"Finding urls of books from {self.__base_url}")
            urls = await self._fetch_book_urls(client_instance)

            self.__logger.info(f"Fetching book details for {len(urls)} URLs")
            results: list[Book] = []
            for i in range(0, len(urls), self.__parallel_calls):
                selected_urls = urls[i : i + self.__parallel_calls]
                results.extend(
                    [
                        book
                        for book in await asyncio.gather(
                            *[
                                self.fetch_book(url, client_instance)
                                for url in selected_urls
                            ]
                        )
                        if book
                    ]
                )

        return results

    # region dependencies: fetch_books

    async def _fetch_book_urls(self, client: HttpClientBase):
        # arrange
        result: list[str] = []
        segment: str = r"/catalogue/fragment?page=1&text=loup%20solitaire"

        while segment:
            # fetch page content
            url = f"{self.__base_url}{segment}"
            json = await client.get_json(url)
            if not json:
                self.__logger.warning(f"No JSON content retrieved for book URL {url}")
                return []

            # parse HTML content to find book detail links
            html = json.get("html", "")
            if html:
                result.extend(self.__list_factory(html).urls(self.__base_url))
            else:
                self.__logger.warning(f"No HTML content found at '{url}'")

            # check for next page URL
            next_url: str | Literal[False] = json.get("next-url", False)
            segment = next_url if next_url else ""

        return result

    # endregion
    async def fetch_book(
        self, url: str, client: HttpClientBase | None = None
    ) -> Book | None:
        book: Book | None = None
        try:
            self.__logger.info(
                f"get book details from : {url}",
            )
            active_client = client or self.__client
            html = await active_client.get_text(url)
            if not html:
                self.__logger.warning(f"No HTML content retrieved for book URL {url}")
                return None

            details = self.__details_factory(html)
            authors = details.authors()
            if "Joe Dever" not in authors:
                self.__logger.warning(
                    f"Skipping book at {url}. It doesn't match authors.",
                )
                return None

            id = numero = details.numero()
            if numero < 0:
                self.__logger.error(
                    f"Could not find a valid book's number at {url}. Defaulting to {numero}.",
                )
            isbn = details.isbn("")
            price, currency = self.__price_details_factory(html).price_and_currency()
            prices = (
                [
                    BookPrice(
                        isbn=isbn,
                        source=self.__base_url,
                        price=round(price, 2),
                        currency=currency,
                        url=url,
                    )
                ]
                if currency != "not set"
                else []
            )

            book = Book(
                id=id,
                url=url,
                numero=numero,
                titre=details.title(""),
                authors=authors,
                lastParutionDate=details.lastParutionDate("1900-01-01"),
                description=details.description(""),
                isbn=isbn,
                image=await details.image(active_client),
                prices=prices,
                official=True,
            )
            UnitTestCapture.capture(
                f"src/usecases/book/tests/dataset/gallimard_{book.isbn}.html",
                html,
            )
        except Exception as e:
            self.__logger.error(
                f"Error while fetching book details for {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return book
