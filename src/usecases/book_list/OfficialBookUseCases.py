import asyncio
import logging
from collections.abc import Callable
from typing import Literal

from domain import Book
from ports.http import HttpClientBase
from ports.usecase import BookDetailsFinderBase, BookListFinderBase


class OfficialBookUseCases:
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        client: HttpClientBase,
        list_factory: Callable[[str], BookListFinderBase],
        details_factory: Callable[[str], BookDetailsFinderBase],
        parallel_calls: int = 5,
    ):
        self.__client = client
        self.__list_factory = list_factory
        self.__details_factory = details_factory
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__parallel_calls = parallel_calls

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        results: list[Book] = []

        active_client = client or self.__client
        async with active_client as client_instance:
            self.__logger.info(f"Finding urls of books from {self._url_base}")
            urls = await self._fetch_book_urls(client_instance)

            self.__logger.info(f"Fetching book details for {len(urls)} URLs")
            results: list[Book] = []
            for i in range(0, len(urls), self.__parallel_calls):
                selected_urls = urls[i : i + self.__parallel_calls]
                tasks = [self.fetch_book(url, client_instance) for url in selected_urls]
                results.extend([book for book in await asyncio.gather(*tasks) if book])

        return results

    # region dependencies: fetch_books

    async def _fetch_book_urls(self, client: HttpClientBase):
        # arrange
        result: list[str] = []
        segment: str = r"/catalogue/fragment?page=1&text=loup%20solitaire"

        while segment:
            # fetch page content
            url = f"{self._url_base}{segment}"
            json = await client.get_json(url)
            if not json:
                self.__logger.warning(f"No JSON content retrieved for book URL {url}")
                return []

            # parse HTML content to find book detail links
            html = json.get("html", "")
            if html:
                result.extend(self.__list_factory(html).urls(self._url_base))
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
                prices=details.prices(url=url, isbn=isbn),
                official=True,
            )
        except Exception as e:
            self.__logger.error(
                f"Error while fetching book details for {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return book
