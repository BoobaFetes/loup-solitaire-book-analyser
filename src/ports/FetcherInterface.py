from typing import Any

import httpx
from bs4 import ResultSet, Tag

from domain import URLContent


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

    def load(self, url: str) -> URLContent:
        """Charger le contenu d'une page HTML.

        Args:
            url (str): L'URL de la page à charger.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            URLContent: Le contenu de la page chargée.
        """
        raise NotImplementedError

    async def load_async(self, url: str, async_client: httpx.AsyncClient) -> URLContent:
        """Charger le contenu d'une page HTML de manière asynchrone.

        Args:
            url (str): L'URL de la page à charger.
            async_client (httpx.AsyncClient): Le client HTTP asynchrone à utiliser.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            URLContent: Le contenu de la page chargée.
        """
        raise NotImplementedError

    def prettify_html(self, html: str) -> str:
        """Préttifier le code HTML.

        Args:
            html (str): Le code HTML à préttifier.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            str: Le code HTML préttifié.
        """
        raise NotImplementedError

    def select_all_by_selector(
        self, content: URLContent, selector: str
    ) -> ResultSet[Tag]:
        """Sélectionner des éléments dans le contenu HTML en utilisant un sélecteur CSS.

        Args:
            content (URLContent): Le contenu HTML à analyser.
            selector (str): Le sélecteur CSS à utiliser pour la sélection.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            ResultSet[Tag]: Les éléments correspondants au sélecteur.
        """
        raise NotImplementedError
