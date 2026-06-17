from abc import ABC, abstractmethod

from ports.usecase.DetailsHtmlFinderBase import DetailsHtmlFinderBase


class PriceDetailsFinderBase(DetailsHtmlFinderBase, ABC):
    @abstractmethod
    def __init__(self, html: str): ...

    @abstractmethod
    def url(self, **kwargs) -> str: ...

    @abstractmethod
    def price_and_currency(self, **kwargs) -> tuple[float, str]: ...
