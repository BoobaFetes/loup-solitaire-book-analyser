from bs4 import ResultSet, Tag

from domain import URLContent


class HTMLReaderInterface:
    def load(self, url: str) -> URLContent:
        raise NotImplementedError

    def prettify_html(self, text: str) -> str:
        raise NotImplementedError

    def select_by_selector(self, content: URLContent, selector: str) -> ResultSet[Tag]:
        raise NotImplementedError
