import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from domain import Book, URLContent
from ports import HTMLReaderInterface, LoggerInterface


class BooksUseCasesOptions:
    def __init__(
        self,
        base_url: str | None = None,
        url: str | None = None,
    ):
        self.base_url = base_url or "https://www.bibliotheque-des-aventuriers.com/"
        self.url = url or self.base_url + "menu/4_serie/loup_solitaire.htm"


class BookUseCases:
    def __init__(
        self,
        html_reader: HTMLReaderInterface,
        logger: LoggerInterface,
        options: BooksUseCasesOptions = BooksUseCasesOptions(),
    ):
        self.__html_reader = html_reader
        self.__logger = logger
        self.__options = options

    # region CRUD

    def update(self, tome: Book) -> bool:
        return self.__repo.update(tome)

    def get(self, numero: int) -> Book:
        return self.__repo.get(numero)

    def find(self, numero: int) -> Book | None:
        return self.__repo.find(numero)

    def list(self) -> list[Book]:
        return self.__repo.list()

    # endregion

    # region logic

    async def find_urls(self) -> list[str]:
        # arrange
        selector = "body > table > tr > td:nth-child(1) > table:nth-child(2) > tr > td:nth-child(2) > table > tr > td > p:nth-child(9) a"

        # load list of books from html
        self.__logger.info("Loading list of books from html", self.__class__.__name__)
        html_list_of_books = self.__html_reader.load(self.__options.url).text

        # find then select all book's names from the list
        soup = BeautifulSoup(html_list_of_books, "html.parser")
        anchors = soup.select(selector)
        self.__logger.info(
            f"Find {len(anchors)} books to download", self.__class__.__name__
        )

        return [
            self.__options.base_url + anchor["href"].replace("../", "")
            for anchor in anchors
        ]

    async def load_async(self, url: str, async_client: httpx.AsyncClient) -> Book:
        try:
            content: URLContent = await self.__html_reader.load_async(url, async_client)

            soup = BeautifulSoup(content.text, "html.parser")
            numero = int(Path(content.url).name.split("_", 1)[0])
            titre_from_html = soup.select_one(
                "table#AutoNumber1 p:nth-child(1)"
            ).get_text(strip=True)
            titre = re.sub(
                r"\(.*\)|Voir.*$", "", titre_from_html, flags=re.DOTALL
            )  # retire les parenthèses et le texte "Voir..." qui suit, présent dans les titres du premier tome qui a 2 versions: "classique" et "augmentée"
            titre = re.sub(r"\s+", " ", titre).strip()  # gère \r\n\t et doubles espaces

            titre_original: str = soup.select_one(
                "table#AutoNumber2 tr:nth-child(2) td:nth-child(2) i"
            ).get_text(strip=True)

            description: str = soup.select_one(
                "table#AutoNumber2 tr:nth-child(3) td p:nth-child(5)"
            ).get_text(strip=True)
            description = re.sub(r"\s+", " ", description).strip()

            self.__logger.debug(
                f"Parsed tome {numero}: '{titre}'", self.__class__.__name__
            )
            return Book(
                numero=numero,
                titre=titre,
                titre_original=titre_original,
                description=description,
            )
        except Exception as e:
            self.__logger.error(
                f"Error loading book from url {url}: {e}", self.__class__.__name__
            )
            raise e

    # endregion
