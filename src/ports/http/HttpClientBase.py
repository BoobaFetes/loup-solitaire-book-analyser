from typing import Generic, Protocol, TypeVar

TJsonResponse = TypeVar("TJsonResponse")


class HttpClientBase(Generic[TJsonResponse], Protocol):
    # region HTTP client lifecycle methods

    async def open(self, **kwargs) -> None:
        raise NotImplementedError("open method not implemented")

    async def close(self) -> None:
        raise NotImplementedError("close method not implemented")

    def enable_cache(self, enabled: bool = True) -> bool:
        raise NotImplementedError("enable_cache method not implemented")

    # endregion

    # region Context manager methods

    async def __aenter__(self):
        await self.open()
        return self  # ← retourne l'instance utilisée dans le "as"

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        await self.close()
        return False  # ← False = ne supprime pas les exceptions

    # endregion

    # region HTTP GET methods

    async def get_json(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> dict[str, TJsonResponse]:
        raise NotImplementedError("get_json method not implemented")

    async def get_text(
        self,
        endpoint: str,
        encoding: str | None = None,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> str:
        raise NotImplementedError("get_text method not implemented")

    async def get_image(
        self,
        endpoint: str,
        retry: int = 3,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        raise NotImplementedError("get_image method not implemented")

    # endregion
