import httpx
from bs4 import ResultSet, Tag

from domain import URLContent


class HTMLReaderInterface:
    def load(self, url: str) -> URLContent:
        raise NotImplementedError

    async def load_async(self, url: str, async_client: httpx.AsyncClient) -> URLContent:
        raise NotImplementedError

    def prettify_html(self, text: str) -> str:
        raise NotImplementedError

    def select_by_selector(self, content: URLContent, selector: str) -> ResultSet[Tag]:
        raise NotImplementedError
