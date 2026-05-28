import asyncio
import re
from typing import cast

import httpx
from bs4 import BeautifulSoup, Tag

from domain import Book
from ports import FetcherInterface
from usecases.BookUseCasesInterface import BookUseCasesInterface


class NonOfficialBookUseCases(BookUseCasesInterface):
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

    async def fetch_books(self, fetcher: FetcherInterface) -> list[Book]:
        results: list[Book] = []
        # attention, le site de la bibliothèque des aventuriers est très lent et instable, il faut prévoir plusieurs tentatives pour éviter les erreurs de timeout ou de connexion
        book_details_attempts = 3
        async with fetcher as fetcher:
            self._logger.info(
                "Fetching main page to find url of books", self.__class__.__name__
            )
            urls = await self._fetch_book_urls(
                fetcher,
            )

            self._logger.info(
                f"Fetching book details for {len(urls)} URLs", self.__class__.__name__
            )
            tasks = [
                self.fetch_book(url, fetcher, book_details_attempts) for url in urls
            ]
            results = [book for book in await asyncio.gather(*tasks) if book]

        return results

    async def _fetch_book_urls(self, fetcher: FetcherInterface):
        # arrange
        index_page_url = self._url_base + r"menu/4_serie/loup_solitaire.htm"

        # fetch page content
        self._logger.debug(
            f"Fetching list of books from: {index_page_url}", self.__class__.__name__
        )
        html = await fetcher.fetch_text_async(index_page_url, "latin-1")

        # parse HTML content to find book detail links
        self._logger.debug(
            "Parsing HTML content for book details page links",
            self.__class__.__name__,
        )
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.select(
            "body > table > tr > td:nth-child(1) > table:nth-child(2) > tr > td:nth-child(2) > table > tr > td > p:nth-child(9) a"
        )

        return [
            self._url_base + str(anchor["href"]).replace("../", "")
            for anchor in anchors
        ]

    # region _get_book method and dependencies functions

    async def fetch_book(
        self, url: str, fetcher: FetcherInterface, attempts: int = 3
    ) -> Book | None:
        book: Book | None = None
        numero_options = {"id": 0}
        try:
            self._logger.debug(
                f"get book details from URL: {url} (attempts left: {attempts})",
                self.__class__.__name__,
            )
            html = await fetcher.fetch_text_async(url, "latin-1")
            soup = BeautifulSoup(html, "html.parser")

            if self._is_classic_version(soup):
                self._logger.debug(
                    "Book is a classic version, skipping to avoid duplicates with official source",
                    self.__class__.__name__,
                )
                return None

            id = numero = self._get_numero(soup, numero_options)
            if numero < 0:
                self._logger.warning(
                    f"Could not find a valid numero for book at URL: {url}. Defaulting to {numero_options['id']}.",
                    self.__class__.__name__,
                )

            book = Book(
                id=id,
                url=url,
                numero=numero,
                titre=self._get_title(soup, ""),
                description=self._get_description(soup, ""),
                isbn=self._get_isbn(soup, ""),
                image=self._get_image(soup, ""),
                prices=[],
                official=False,
            )
        except httpx.ConnectTimeout as e:
            self._logger.warning(
                f"Connection timeout while fetching book details for URL: {url}",
                self.__class__.__name__,
            )
            if attempts > 0:
                self._logger.info(
                    f"Retrying to fetch {url}: ({attempts} attempts left)",
                    self.__class__.__name__,
                )
            else:
                raise e
        except Exception as e:
            self._logger.error(
                f"Error while fetching book details for URL: {url} - {e}",
                self.__class__.__name__,
            )

        if not book and attempts > 0:
            return await self.fetch_book(url, fetcher, attempts - 1)
        return book

    def _get_numero(self, soup: BeautifulSoup, options: dict[str, int]) -> int:
        # arrange
        text_prefix = "loup solitaire n° "
        selector = "table#AutoNumber2 tr:nth-child(2) > td:nth-child(2) a"

        # action
        element = soup.select_one(selector)
        if element:
            text = element.get_text(strip=True)
            if text.lower().startswith(text_prefix):
                numero = text[len(text_prefix) :]
                if numero.isdigit():
                    return int(numero)

        options["id"] -= 1
        return options["id"]

    def _get_title(self, soup: BeautifulSoup, default_value: str) -> str:
        element = soup.select_one("table#AutoNumber1 p:nth-child(1)")
        if not element:
            return default_value

        titre = element.get_text(strip=True)
        # retire les parenthèses et le texte "Voir..." qui suit, présent dans les titres du premier tome qui a 2 versions: "classique" et "augmentée"
        titre = re.sub(r"\(.*\)|Voir.*$", "", titre, flags=re.DOTALL)

        # gère \r\n\t et doubles espaces
        titre = re.sub(r"\s+", " ", titre).strip()

        return titre

    def _get_isbn(self, soup: BeautifulSoup, default_value: str) -> str:
        root = soup.select_one("table#AutoNumber2 tr:nth-child(2) > td:nth-child(2)")
        if not root:
            return default_value

        # les details du livre sur ce site est sois directement dans le <td /> soit dans un 'p' (<td><p></td>)
        children = list([e for e in root.children if not isinstance(e, str)])
        if len(children) == 1 and cast(Tag, children[0]).name == "p":
            root = cast(Tag, children[0])

        isbn_list: list[str] = []
        texts = [
            e.get_text(strip=True) for e in root.children if not isinstance(e, str)
        ]
        valid_texts = [t for t in texts if t.count("-")]

        for text in valid_texts:
            value: str = NonOfficialBookUseCases.find_first_isbn(text)
            if value:
                isbn_list.append(value.replace("-", ""))

        return isbn_list[-1] if len(isbn_list) and isbn_list[-1] else default_value

    def _get_description(self, soup: BeautifulSoup, default_value: str) -> str:
        element = soup.select_one("table#AutoNumber2 tr:nth-child(3) td p:nth-child(5)")
        if not element:
            return default_value
        description = element.get_text(strip=True)  # type: ignore
        description = re.sub(r"\s+", " ", description).strip()
        return description

    def _get_image(self, soup: BeautifulSoup, default_value: str = "") -> str:
        return ""

    def _is_classic_version(self, soup: BeautifulSoup) -> bool:
        element = soup.select_one("table#AutoNumber1 p:nth-child(1)")
        if not element:
            return False

        titre = element.get_text(strip=True)
        return "classique)" in titre.lower()

    # endregion

    # endregion

    def get_total_and_average_by_currency(self) -> dict[str, tuple[float, float]]:
        raise NotImplementedError
