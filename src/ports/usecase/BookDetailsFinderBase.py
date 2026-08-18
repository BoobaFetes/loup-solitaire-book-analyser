from abc import ABC, abstractmethod

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

    async def _fetch_image(self, client: HttpClientBase, url: str) -> tuple[str, bytes]:
        if not url:
            return "", b""
        image_bytes = await client.get_image(url)
        return url, image_bytes

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
    async def image(self, client: HttpClientBase, **kwargs) -> tuple[str, bytes]: ...

    @abstractmethod
    def is_classic_version(self) -> bool: ...
