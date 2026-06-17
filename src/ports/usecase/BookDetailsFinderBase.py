import base64
from abc import ABC, abstractmethod

from domain import BookPrice
from ports.http import HttpClientBase
from ports.usecase.DetailsHtmlFinderBase import DetailsHtmlFinderBase


class BookDetailsFinderBase(DetailsHtmlFinderBase, ABC):
    __invalid_numero: int = 0

    @staticmethod
    def _get_invalid_numero() -> int:
        BookDetailsFinderBase.__invalid_numero -= 1
        return BookDetailsFinderBase.__invalid_numero

    @abstractmethod
    def __init__(self, html: str): ...

    async def _fetch_image(self, client: HttpClientBase, url: str) -> str:
        if not url:
            return ""
        image_bytes = await client.get_content(url)
        return base64.b64encode(image_bytes).decode("utf-8")

    @abstractmethod
    def isbn(self, default: str) -> str: ...

    @abstractmethod
    def numero(self) -> int: ...

    @abstractmethod
    def title(self, default: str) -> str: ...

    @abstractmethod
    def authors(self) -> list[str]: ...

    @abstractmethod
    def lastParutionDate(self, default: str) -> str: ...

    @abstractmethod
    def description(self, default: str) -> str: ...

    @abstractmethod
    def official(self) -> bool: ...

    @abstractmethod
    def prices(self, **kwargs) -> list[BookPrice]: ...

    @abstractmethod
    async def image(self, client: HttpClientBase, **kwargs) -> str: ...

    @abstractmethod
    def is_classic_version(self) -> bool: ...
