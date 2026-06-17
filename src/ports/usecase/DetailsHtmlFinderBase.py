from abc import ABC, abstractmethod


class DetailsHtmlFinderBase(ABC):
    @abstractmethod
    def __init__(self, html: str): ...
