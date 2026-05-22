import logging
from typing import Any

import httpx
from bs4 import BeautifulSoup, ResultSet, Tag

from domain import URLContent
from ports import HTMLReaderInterface, LoggerInterface


class HttpxLogHandler(logging.Handler):
    def __init__(self, logger: LoggerInterface):
        super().__init__()
        self.__logger = logger

    def emit(self, record: Any) -> None:
        record.msg = f"[{record.args[0]}] [{record.args[3]}] {record.args[4]} - {record.args[2]} - {record.args[1]}"
        record.args = ()  # Clear args to prevent httpx from trying to format the message
        self.__logger.info(record.getMessage(), HTMLReaderAdapter.__name__)


class HTMLReaderAdapter(HTMLReaderInterface):
    """Adaptateur pour l'interface de lecture HTML.

    Args:
        HTMLReaderInterface: L'interface de lecture HTML.
    """

    def __init__(self, logger: LoggerInterface):
        self.__logger: LoggerInterface = logger
        # Prendre le contrôle des logs httpx
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.addHandler(HttpxLogHandler(logger))
        httpx_logger.propagate = False  # empêche la propagation au logger root

    async def load_async(self, url: str, async_client: httpx.AsyncClient) -> URLContent:
        """Load content from a URL asynchronously.

        Args:
            url (str): The URL to load.
            async_client (httpx.AsyncClient): The HTTP client to use.

        Returns:
            URLContent: The content loaded from the URL.
        """
        try:
            response = await async_client.get(
                url
            )  # utilise le client passé en paramètre
            response.raise_for_status()
            return URLContent(url=url, text=response.content.decode("latin-1"))
        except httpx.RequestError as e:
            self.__logger.error(f"Request error occurred: {e}", self.__class__.__name__)
            raise
        except httpx.HTTPStatusError as e:
            self.__logger.error(
                f"HTTP status error occurred: {e}", self.__class__.__name__
            )
            raise
        except httpx.HTTPError as e:
            self.__logger.error(f"HTTP error occurred: {e}", self.__class__.__name__)
            raise
        except Exception as e:
            self.__logger.error(
                f"Unexpected error occurred: {e}", self.__class__.__name__
            )
            raise

    def load(self, url: str) -> URLContent:
        """Load content from a URL.

        Args:
            url (str): The URL to load.

        Returns:
            URLContent: The content loaded from the URL.
        """
        try:
            response = httpx.get(url)
            response.raise_for_status()
            return URLContent(url=url, text=response.content.decode("latin-1"))
        except httpx.RequestError as e:
            self.__logger.error(f"Request error occurred: {e}", self.__class__.__name__)
            raise
        except httpx.HTTPStatusError as e:
            self.__logger.error(
                f"HTTP status error occurred: {e}", self.__class__.__name__
            )
            raise
        except httpx.HTTPError as e:
            self.__logger.error(f"HTTP error occurred: {e}", self.__class__.__name__)
            raise
        except Exception as e:
            self.__logger.error(
                f"Unexpected error occurred: {e}", self.__class__.__name__
            )
            raise

    def prettify_html(self, html: str) -> str:
        """Prettify the HTML content.

        Args:
            html (str): The HTML content to prettify.

        Returns:
            str: The prettified HTML content.
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.prettify()

    def select_by_selector(self, content: URLContent, selector: str) -> ResultSet[Tag]:
        """Select elements from the HTML content using a CSS selector.

        Args:
            content (URLContent): The HTML content to search.
            selector (str): The CSS selector to use for selection.

        Returns:
            ResultSet[Tag]: The elements matching the selector.
        """
        self.__logger.info(
            f"Listing all elements matching selector: {selector}",
            self.__class__.__name__,
        )
        soup = BeautifulSoup(content.text, "html.parser")
        elements = soup.select(selector)
        return elements
