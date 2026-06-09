from typing import List

from domain import BookPrice


class BookPriceRepositoryInterface:
    """Contrat (port) pour un dépôt de book price.

    Les usecases appelleront ces méthodes sans connaître l'implémentation.
    """

    def clear(self) -> bool:
        """Effacer tous les book prices du dépôt.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le dépôt a été vidé avec succès, False sinon.
        """
        raise NotImplementedError

    def list(self, isbn: str) -> List[BookPrice]:
        """Retourner la liste de tous les book prices pour un ISBN donné.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            List[BookPrice]: La liste de tous les book prices pour l'ISBN donné.
        """
        raise NotImplementedError

    def get(self, isbn: str, source: str, date: str | None = None) -> BookPrice:
        """Récupérer un book price par son identifiant unique.

        Args:
            id (int): L'identifiant unique du book price à récupérer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            BookPrice: Le book price correspondant à l'identifiant.
        """
        raise NotImplementedError

    def find(self, isbn: str, source: str, date: str | None = None) -> BookPrice | None:
        """Trouver un book price par son identifiant unique.

        Args:
            id (int): L'identifiant unique du book price à trouver.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            BookPrice | None: Le book price correspondant à l'identifiant, ou None s'il n'existe pas.
        """
        raise NotImplementedError

    def add_many(self, prices: List[BookPrice]) -> int:
        """Ajouter plusieurs book prices au dépôt.

        Args:
            prices (List[BookPrice]): La liste des book prices à ajouter.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de book prices ajoutés.
        """
        raise NotImplementedError

    def add(self, price: BookPrice) -> bool:
        """Ajouter un book price au dépôt.

        Args:
            price (BookPrice): Le book price à ajouter.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book price a été ajouté, False sinon.
        """
        raise NotImplementedError

    def update_many(self, prices: List[BookPrice]) -> int:
        """Mettre à jour plusieurs book prices dans le dépôt.

        Args:
            book_prices (List[BookPrice]): La liste des book prices à mettre à jour.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de book prices mis à jour.
        """
        raise NotImplementedError

    def update(self, price: BookPrice) -> bool:
        """Mettre à jour un book price existant dans le dépôt.

        Args:
            book_price (BookPrice): Le book price à mettre à jour.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book price a été mis à jour avec succès, False sinon.
        """
        raise NotImplementedError

    def delete_many(self, prices: List[BookPrice]) -> int:
        """Supprimer plusieurs book prices du dépôt par leurs identifiants uniques.

        Args:
            ids (List[int]): La liste des identifiants uniques des book prices à supprimer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de book prices supprimés.
        """
        raise NotImplementedError

    def delete(self, price: BookPrice) -> bool:
        """Supprimer un book price du dépôt par son identifiant unique.

        Args:
            id (int): L'identifiant unique du book price à supprimer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book price a été supprimé avec succès, False sinon.
        """
        raise NotImplementedError
