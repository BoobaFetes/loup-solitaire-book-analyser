import logging

from bs4 import BeautifulSoup

from ports.usecase import BookListFinderBase


class GallimardBookListFinder(BookListFinderBase):
    def __init__(self, html: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__soup = BeautifulSoup(html, "html.parser")

    def urls(self, base_url: str, **kwargs) -> list[str]:
        anchors = self.__soup.select("p.BookItem-title > a")
        return [f"{base_url}{str(a['href'])}" for a in anchors if a.has_attr("href")]
