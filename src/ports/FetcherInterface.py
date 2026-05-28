from typing import Any


class FetcherInterface:
    # region Context manager methods

    async def __aenter__(self):
        return self  # ← retourne l'instance utilisée dans le "as"

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        return False  # ← False = ne supprime pas les exceptions

    # endregion

    async def fetch_json_async(self, url: str) -> dict[str, Any]:
        raise NotImplementedError

    async def fetch_text_async(self, url: str, encoding: str | None = None) -> str:
        raise NotImplementedError

    async def fetch_content_async(self, url: str) -> bytes:
        raise NotImplementedError
