import logging

from bs4 import BeautifulSoup

from ports.usecase import BookListFinderBase


class BiblioAventurierBookListFinder(BookListFinderBase):
    def __init__(self, html: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__soup = BeautifulSoup(html, "html.parser")

    def urls(self, base_url: str, **kwargs) -> list[str]:
        anchors = self.__soup.select(
            "body > table > tr > td:nth-child(1) > table:nth-child(2) > tr > td:nth-child(2) > table > tr > td > p:nth-child(9) a"
        )

        return [base_url + str(anchor["href"]).replace("../", "") for anchor in anchors]
