from bs4 import BeautifulSoup

from domain import URLContent
from ports import FileSystemInterface, HTMLReaderInterface, LoggerInterface


class ListOfBooksUseCasesOptions:
    def __init__(
        self,
    ):
        self.base_url = "https://www.bibliotheque-des-aventuriers.com/"
        self.url = self.base_url + "menu/4_serie/loup_solitaire.htm"


class ListOfBooksUseCases:
    def __init__(
        self,
        html_reader: HTMLReaderInterface,
        fs: FileSystemInterface,
        logger: LoggerInterface,
    ):
        self.__html_reader = html_reader
        self.__fs = fs
        self.__logger = logger
        self.__options = ListOfBooksUseCasesOptions()

    def load(self) -> list[URLContent]:
        # arrange
        contents: list[URLContent] = []
        selector = "body > table > tr > td:nth-child(1) > table:nth-child(2) > tr > td:nth-child(2) > table > tr > td > p:nth-child(9) a"

        # load list of books from html
        self.__fs.clear("*.html")
        self.__logger.info("Loading list of books from html", self.__class__.__name__)
        html_list_of_books = self.__html_reader.load(self.__options.url).text

        # find then select all book's names from the list
        soup = BeautifulSoup(html_list_of_books, "html.parser")
        anchors = soup.select(selector)
        self.__logger.info(
            f"Find {len(anchors)} books to download", self.__class__.__name__
        )

        # load each book from html
        for anchor in anchors:
            url = self.__options.base_url + anchor["href"].replace("../", "")
            contents.append(self.__html_reader.load(url))

        return contents
