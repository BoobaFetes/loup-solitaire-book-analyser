from typing import Generic, TypeVar

TResponse = TypeVar("TResponse")
TData = TypeVar("TData")


class HttpClientBase(Generic[TResponse, TData]):
    # region HTTP client lifecycle methods

    async def open(self, **kwargs) -> None:
        raise NotImplementedError("open method not implemented")

    async def close(self) -> None:
        raise NotImplementedError("close method not implemented")

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

    async def get_json(self, endpoint: str, retry: int = 3) -> dict[str, TResponse]:
        raise NotImplementedError("get_json method not implemented")

    async def get_text(
        self, endpoint: str, encoding: str | None = None, retry: int = 3
    ) -> str:
        raise NotImplementedError("get_text method not implemented")

    async def get_content(self, endpoint: str, retry: int = 3) -> bytes:
        raise NotImplementedError("get_content method not implemented")

    # endregion
