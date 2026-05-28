import logging
from typing import Any

import httpx

from ports import FetcherInterface, LoggerInterface


class HttpxLogHandler(logging.Handler):
    __is_setup_done = False

    @classmethod
    def setup(cls, logger: LoggerInterface, logger_name: str | None = None):
        if cls.__is_setup_done:
            return

        # Configure logging for httpx requests.
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.addHandler(HttpxLogHandler(logger, "FetcherAdapter"))
        httpx_logger.propagate = False  # Prevent propagation to the root logger
        cls.__is_setup_done = True

    def __init__(self, logger: LoggerInterface, logger_name: str | None = None):
        super().__init__()
        self.__logger = logger
        self.__logger_name = logger_name or logger.__class__.__name__

    def emit(self, record: logging.LogRecord) -> None:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 5:
            record.msg = f"[{args[0]}] [{args[3]}] {args[4]} - {args[2]} - {args[1]}"
            record.args = ()  # Clear args to prevent httpx from trying to format the message
            self.__logger.info(record.getMessage(), self.__logger_name)


class FetcherAdapter(FetcherInterface):
    """Adaptateur pour l'interface de lecture HTML.

    Args:
        FetcherInterface: L'interface de lecture HTML.
    """

    def __init__(self, logger: LoggerInterface):
        self.__logger: LoggerInterface = logger
        HttpxLogHandler.setup(logger, "FetcherAdapter")

    # region Context manager methods

    async def __aenter__(self):
        self._client = httpx.AsyncClient()
        return self  # ← retourne l'instance utilisée dans le "as"

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        await self._client.aclose()
        return False  # ← False = ne supprime pas les exceptions

    # endregion

    async def fetch_json_async(self, url: str) -> dict[str, Any]:
        """Fetch JSON data from a URL.

        Args:
            url (str): The URL to fetch.

        Errors:
            httpx.ConnectTimeout: If a connection timeout occurs.
            httpx.ConnectError: If a connection error occurs.
            httpx.RequestError: If a request error occurs.
            httpx.HTTPStatusError: If an HTTP status error occurs.
            httpx.HTTPError: If a general HTTP error occurs.
            Exception: If an unexpected error occurs.

        Returns:
            dict[str, Any]: The JSON response from the server.
        """
        response = await self._fetch(url)
        return response.json()

    async def fetch_text_async(self, url: str, encoding: str | None = None) -> str:
        """Fetch text data from a URL.

        Args:
            url (str): The URL to fetch.

        Errors:
            httpx.ConnectTimeout: If a connection timeout occurs.
            httpx.ConnectError: If a connection error occurs.
            httpx.RequestError: If a request error occurs.
            httpx.HTTPStatusError: If an HTTP status error occurs.
            httpx.HTTPError: If a general HTTP error occurs.
            Exception: If an unexpected error occurs.

        Returns:
            str: The text response from the server.
        """
        response = await self._fetch(url)
        if not encoding:
            return response.text  # httpx will use the charset from the response headers or fallback to utf-8
        else:
            return response.content.decode(
                encoding
            )  # decode the content with the specified encoding

    async def fetch_content_async(self, url: str) -> bytes:
        """Fetch content data from a URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            bytes: The content response from the server.
        """
        response = await self._fetch(url)
        return response.content

    # region private methods to call

    async def _fetch(self, url: str) -> httpx.Response:
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            return response
        except httpx.ConnectTimeout as e:
            self.__logger.critical(
                f"Connection timeout occurred: {e or 'not set'}",
                self.__class__.__name__,
            )
            raise
        except httpx.ConnectError as e:
            self.__logger.critical(
                f"Connection error occurred: {e or 'not set'}", self.__class__.__name__
            )
            raise
        except httpx.RequestError as e:
            self.__logger.critical(
                f"Request error occurred: {e or 'not set'}", self.__class__.__name__
            )
            raise
        except httpx.HTTPStatusError as e:
            self.__logger.critical(
                f"HTTP status error occurred: {e or 'not set'}", self.__class__.__name__
            )
            raise
        except httpx.HTTPError as e:
            self.__logger.critical(
                f"HTTP error occurred: {e or 'not set'}", self.__class__.__name__
            )
            raise
        except Exception as e:
            self.__logger.critical(
                f"Unexpected error occurred: {e or 'not set'}", self.__class__.__name__
            )
            raise

    # endregion
