import asyncio
import json
import logging
from typing import TypeVar, cast

import httpx

from adapters.http.HttpxLogHandler import HttpxLogHandler
from ports.cache import InMemoryCacheInterface
from ports.http import HttpClientBase

TJsonResponse = TypeVar("TJsonResponse")


class HttpClientAdapter(HttpClientBase[TJsonResponse]):
    def __init__(
        self, inmemory_cache: InMemoryCacheInterface, retry_delay: float = 1.0, **kwargs
    ):
        self.__inmemory_cache = inmemory_cache
        self.__cache_enabled = self.__inmemory_cache.is_enabled()
        self.__retry_delay = retry_delay
        self.client_options = kwargs
        self.__client: httpx.AsyncClient | None = None

        # manages logger configuration for this adapter and httpx logs
        self.__logger = logging.getLogger(self.__class__.__name__)
        HttpxLogHandler.setup(self.__class__.__name__)

    # region HTTP client lifecycle methods
    async def open(self, **kwargs) -> None:
        if self.__client and not self.__client.is_closed:
            return  # Client déjà ouvert

        options = {**self.client_options, **kwargs}
        self.__client = httpx.AsyncClient(**options)
        self.__logger.info(f"HTTP async client opened with options: {options}")

    async def close(self) -> None:
        if not self.__client or self.__client.is_closed:
            return  # Client déjà fermé

        await self.__client.aclose()
        self.__client = None
        self.__logger.info("HTTP async client closed")

    def enable_cache(self, enabled: bool = True) -> bool:
        previous_value = self.__cache_enabled
        self.__cache_enabled = enabled and self.__inmemory_cache.is_enabled()
        return previous_value

    # endregion

    # region HTTP GET methods

    # region private methods managing response errors and retry
    async def __get(
        self, endpoint: str, retry: int, headers: dict[str, str] | None = None
    ) -> httpx.Response:
        response: httpx.Response = cast(httpx.Response, None)
        try:
            if not self.__client or self.__client.is_closed:
                raise RuntimeError("HTTP client is not open")

            response = await self.__client.get(endpoint, headers=headers)
            response.raise_for_status()
            return response
        except RuntimeError as e:
            self.__logger.critical(
                f"Runtime error occurs for {endpoint}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except httpx.ConnectTimeout as e:
            if retry > 0:
                return await self._retry(endpoint, retry - 1, headers=headers)

            self.__logger.critical(
                f"Connection timeout for {response.url}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except httpx.ConnectError as e:
            if retry > 0:
                return await self._retry(endpoint, retry - 1, headers=headers)

            self.__logger.critical(
                f"Connection error for {response.url}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except httpx.ReadTimeout as e:
            if retry > 0:
                return await self._retry(endpoint, retry - 1, headers=headers)

            self.__logger.critical(
                f"Read timeout for {response.url}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except httpx.ReadError as e:
            if retry > 0:
                return await self._retry(endpoint, retry - 1, headers=headers)

            self.__logger.critical(
                f"Read error for {response.url}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except httpx.HTTPStatusError as e:
            self.__logger.critical(
                f"Bad request HTTP status code {e.response.status_code} for {e.request.url}: {e.response.text} - {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except httpx.RequestError as e:
            self.__logger.critical(
                f"Request error for {e.request.url}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except Exception as e:
            self.__logger.critical(
                f"Unexpected error for {response.url}: {type(e).__name__}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise

    async def _retry(
        self, endpoint: str, retry: int, headers: dict[str, str] | None = None
    ) -> httpx.Response:
        self.__logger.warning(
            f"Retrying to fetch after {self.__retry_delay} seconds - retry left: {retry} - URL: {endpoint}",
        )
        await asyncio.sleep(self.__retry_delay)
        return await self.__get(endpoint, retry, headers=headers)

    # endregion

    async def get_json(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> dict[str, TJsonResponse]:
        if self.__cache_enabled:
            content = self.__inmemory_cache.get(endpoint)
            if content:
                try:
                    return json.loads(cast(str, content))
                except json.JSONDecodeError:
                    self.__logger.warning(
                        f"Ignoring invalid cached JSON for {endpoint}"
                    )

        response = await self.__get(endpoint, retry, headers=headers)
        result = response.json()

        if self.__cache_enabled:
            self.__inmemory_cache.set_background(endpoint, json.dumps(result))

        return result

    async def get_text(
        self,
        endpoint: str,
        encoding: str | None = None,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> str:
        if self.__cache_enabled:
            content = self.__inmemory_cache.get(endpoint)
            if content:
                return cast(str, content)

        response = await self.__get(endpoint, retry, headers=headers)
        result = response.text if not encoding else response.content.decode(encoding)

        if self.__cache_enabled:
            self.__inmemory_cache.set_background(endpoint, result)

        return result

    async def get_image(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        response = await self.__get(endpoint, retry, headers=headers)
        return response.content

    # endregion
