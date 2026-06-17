from abc import ABC, abstractmethod

from ports.usecase.DetailsHtmlFinderBase import DetailsHtmlFinderBase


class BookListFinderBase(DetailsHtmlFinderBase, ABC):
    @abstractmethod
    def __init__(self, html: str): ...

    @abstractmethod
    def urls(self, base_url: str, **kwargs) -> list[str]: ...
