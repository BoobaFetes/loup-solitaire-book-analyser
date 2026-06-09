import asyncio
import logging
import re

from bs4 import BeautifulSoup

from domain import Book
from ports import BookRepositoryInterface, HttpClientBase
from usecases.book_list.NonOfficialBookDetails import NonOfficialBookDetails


class NonOfficialBookUseCases:
    """Use cases for managing books."""

    _url_base: str = "https://www.bibliotheque-des-aventuriers.com/"

    _isbn_matchers = [
        # should match ISBN 13: 978-2-07-064302-7
        re.compile(r"([\d]{3}-[\d]{1}-[\d]{2}-[\d]{6}-[\d]{1})"),
        # should match ISBN 10: 2-07-064302-7, 2-07-057492-X (X can be a digit or a letter, X is used as 10 in ISBN 10 see official documentation for more details)
        re.compile(r"([\d]{1}-[\d]{2}-[\d]{6}-[\dX]{1})"),
    ]

    @staticmethod
    def find_first_isbn(text: str) -> str:
        for matcher in NonOfficialBookUseCases._isbn_matchers:
            regexp_match = matcher.search(text)
            if regexp_match:
                value = regexp_match.group(1)
                if value:
                    return value.replace("-", "")

        return ""

    def __init__(
        self,
        repository: BookRepositoryInterface,
        client: HttpClientBase,
        parallel_calls: int = 5,
    ):
        self._repository = repository
        self._client = client
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

        # parse HTML content to find book detail links
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.select(
            "body > table > tr > td:nth-child(1) > table:nth-child(2) > tr > td:nth-child(2) > table > tr > td > p:nth-child(9) a"
        )

        return [
            self._url_base + str(anchor["href"]).replace("../", "")
            for anchor in anchors
        ]

    # endregion

    async def fetch_book(
        self, url: str, client: HttpClientBase | None = None
    ) -> Book | None:
        book: Book | None = None
        numero_options = {"id": 0}
        try:
            self._logger.info(
                f"get book details from : {url}",
            )

            active_client = client or self._client
            html = await active_client.get_text(url, "latin-1")
            if not html:
                self._logger.warning(f"No HTML content retrieved for book URL {url}")
                return None

            soup = BeautifulSoup(html, "html.parser")

            details = NonOfficialBookDetails(soup)
            if details.is_classic_version():
                self._logger.info(
                    "Book is a classic version, skipping to avoid duplicates with official source",
                )
                return None

            id = numero = details.numero(numero_options)
            if numero < 0:
                self._logger.error(
                    f"Could not find a valid book's number at {url}. Defaulting to {numero_options['id']}.",
                )

            image = await details.image_url(active_client, self._url_base, "")
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
                lastParutionDate=details.last_parution_date("1900-01-01"),
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

    def get_total_and_average_by_currency(self) -> dict[str, tuple[float, float]]:
        raise NotImplementedError
