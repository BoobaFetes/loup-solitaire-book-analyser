from typing import List

from domain import Book


class BookRepositoryInterface:
    """Contrat (port) pour un dépôt de Tome.

    Les usecases appelleront ces méthodes sans connaître l'implémentation.
    """

    def list(self) -> List[Book]:
        """Retourner la liste de tous les tomes.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            List[Book]: La liste de tous les tomes.
        """
        raise NotImplementedError

    def add_many(self, tomes: List[Book]) -> int:
        """Ajouter plusieurs tomes au dépôt.

        Args:
            tomes (List[Book]): La liste des tomes à ajouter.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de tomes ajoutés.
        """
        raise NotImplementedError

    def add(self, tome: Book) -> bool:
        """Ajouter un tome au dépôt.

        Args:
            tome (Book): Le tome à ajouter.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le tome a été ajouté, False sinon.
        """
        raise NotImplementedError

    def get(self, numero: int) -> Book:
        """Récupérer un tome par son numéro.

        Args:
            numero (int): Le numéro du tome à récupérer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            Book: Le tome correspondant au numéro.
        """
        raise NotImplementedError

    def find(self, numero: int) -> Book | None:
        """Trouver un tome par son numéro.

        Args:
            numero (int): Le numéro du tome à trouver.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            Book | None: Le tome correspondant au numéro, ou None s'il n'existe pas.
        """
        raise NotImplementedError

    def update(self, tome: Book) -> bool:
        """Mettre à jour un tome existant dans le dépôt.

        Args:
            tome (Book): Le tome à mettre à jour.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le tome a été mis à jour avec succès, False sinon.
        """
        raise NotImplementedError

    def delete(self, numero: int) -> bool:
        """Supprimer un tome du dépôt par son numéro.

        Args:
            numero (int): Le numéro du tome à supprimer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le tome a été supprimé avec succès, False sinon.
        """
        raise NotImplementedError
