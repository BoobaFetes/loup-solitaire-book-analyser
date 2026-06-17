import asyncio
import logging
from collections.abc import Callable

from domain import Book
from ports.http import HttpClientBase
from ports.usecase import BookDetailsFinderBase, BookListFinderBase


class NonOfficialBookUseCases:
    """Use cases for managing books."""

    _url_base: str = "https://www.bibliotheque-des-aventuriers.com/"

    def __init__(
        self,
        client: HttpClientBase,
        list_factory: Callable[[str], BookListFinderBase],
        details_factory: Callable[[str], BookDetailsFinderBase],
        parallel_calls: int = 5,
    ):
        self._client = client
        self.__list_factory = list_factory
        self._details_factory = details_factory
        self._logger = logging.getLogger(self.__class__.__name__)
        self._parallel_calls = parallel_calls

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        results: list[Book] = []

        active_client = client or self._client
        async with active_client as client_instance:
            self._logger.info(f"Finding urls of books from {self._url_base}")
            urls = await self._fetch_book_urls(client_instance)

            self._logger.info(f"Fetching book details for {len(urls)} URLs")
            results: list[Book] = []
            for i in range(0, len(urls), self._parallel_calls):
                selected_urls = urls[i : i + self._parallel_calls]
                tasks = [self.fetch_book(url, client_instance) for url in selected_urls]
                results.extend([book for book in await asyncio.gather(*tasks) if book])

        return results

    # region dependencies: fetch_books

    async def _fetch_book_urls(self, client: HttpClientBase):
        # arrange
        index_page_url = self._url_base + r"menu/4_serie/loup_solitaire.htm"

        # fetch page content
        html = await client.get_text(index_page_url, "latin-1")
        if not html:
            self._logger.warning(
                f"No HTML content retrieved for index page {index_page_url}"
            )
            return []

        return self.__list_factory(html).urls(self._url_base)

    # endregion

    async def fetch_book(
        self, url: str, client: HttpClientBase | None = None
    ) -> Book | None:
        book: Book | None = None
        try:
            self._logger.info(
                f"get book details from : {url}",
            )

            active_client = client or self._client
            html = await active_client.get_text(url, "latin-1")
            if not html:
                self._logger.warning(f"No HTML content retrieved for book URL {url}")
                return None

            details = self._details_factory(html)
            if details.is_classic_version():
                self._logger.info(
                    "Book is a classic version, skipping to avoid duplicates with official source",
                )
                return None

            id = numero = details.numero()
            if numero < 0:
                self._logger.error(
                    f"Could not find a valid book's number at {url}. Defaulting to {numero}.",
                )

            image = await details.image(active_client, url_base=self._url_base)
            if not image:
                self._logger.warning(
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
            self._logger.error(
                f"Error while fetching book details for {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return book
