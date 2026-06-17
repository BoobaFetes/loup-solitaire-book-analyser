import asyncio
import logging
from collections.abc import Callable

from domain import Book
from ports.http import HttpClientBase
from ports.usecase import BookDetailsFinderBase, BookListFinderBase


class NonOfficialBookUseCases:
    """Use cases for managing books."""

    def __init__(
        self,
        base_url: str,
        client: HttpClientBase,
        list_factory: Callable[[str], BookListFinderBase],
        details_factory: Callable[[str], BookDetailsFinderBase],
        parallel_calls: int = 5,
    ):
        self.__url_base = base_url
        self.__client = client
        self.__list_factory = list_factory
        self.__details_factory = details_factory
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__parallel_calls = parallel_calls

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        results: list[Book] = []

        active_client = client or self.__client
        async with active_client as client_instance:
            self.__logger.info(f"Finding urls of books from {self.__url_base}")
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
        index_page_url = self.__url_base + r"menu/4_serie/loup_solitaire.htm"

        # fetch page content
        html = await client.get_text(index_page_url, "latin-1")
        if not html:
            self.__logger.warning(
                f"No HTML content retrieved for index page {index_page_url}"
            )
            return []

        return self.__list_factory(html).urls(self.__url_base)

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
            html = await active_client.get_text(url, "latin-1")
            if not html:
                self.__logger.warning(f"No HTML content retrieved for book URL {url}")
                return None

            details = self.__details_factory(html)
            if details.is_classic_version():
                self.__logger.info(
                    "Book is a classic version, skipping to avoid duplicates with official source",
                )
                return None

            id = numero = details.numero()
            if numero < 0:
                self.__logger.error(
                    f"Could not find a valid book's number at {url}. Defaulting to {numero}.",
                )

            image = await details.image(active_client, base_url=self.__url_base)
            if not image:
                self.__logger.warning(
                    f"No image content fetched for book URL: {url}",
                )

            book = Book(
                id=id,
                url=url,
                numero=numero,
                titre=details.title(""),
                authors=details.authors(),
                lastParutionDate=details.lastParutionDate("1900-01-01"),
                description=details.description(""),
                isbn=details.isbn(""),
                image=image,
                prices=[],
                official=False,
            )
        except Exception as e:
            self.__logger.error(
                f"Error while fetching book details for {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return book
