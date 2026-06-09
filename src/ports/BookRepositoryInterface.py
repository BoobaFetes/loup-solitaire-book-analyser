from typing import List

from domain import Book


class BookRepositoryInterface:
    """Contrat (port) pour un dépôt de book.

    Les usecases appelleront ces méthodes sans connaître l'implémentation.
    """

    def clear(self) -> bool:
        """Effacer tous les books du dépôt.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le dépôt a été vidé avec succès, False sinon.
        """
        raise NotImplementedError

    def list(self) -> List[Book]:
        """Retourner la liste de tous les books.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            List[Book]: La liste de tous les books.
        """
        raise NotImplementedError

    def upsert_many(self, books: List[Book]) -> int:
        """Ajouter ou mettre à jour plusieurs books dans le dépôt.

        Args:
            books (List[Book]): La liste des books à ajouter ou mettre à jour.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de books ajoutés ou mis à jour.
        """
        raise NotImplementedError

    def upsert(self, book: Book) -> bool:
        """Ajouter ou mettre à jour un book dans le dépôt.

        Args:
            book (Book): Le book à ajouter ou mettre à jour.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book a été ajouté ou mis à jour avec succès, False sinon.
        """
        raise NotImplementedError

    def get(self, id: int) -> Book:
        """Récupérer un book par son identifiant unique.

        Args:
            id (int): L'identifiant unique du book à récupérer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            Book: Le book correspondant à l'identifiant.
        """
        raise NotImplementedError

    def find(self, id: int) -> Book | None:
        """Trouver un book par son identifiant unique.

        Args:
            id (int): L'identifiant unique du book à trouver.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            Book | None: Le book correspondant à l'identifiant, ou None s'il n'existe pas.
        """
        raise NotImplementedError

    def update_many(self, books: List[Book]) -> int:
        """Mettre à jour plusieurs books dans le dépôt.

        Args:
            books (List[Book]): La liste des books à mettre à jour.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de books mis à jour.
        """
        raise NotImplementedError

    def update(self, book: Book) -> bool:
        """Mettre à jour un book existant dans le dépôt.

        Args:
            book (Book): Le book à mettre à jour.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book a été mis à jour avec succès, False sinon.
        """
        raise NotImplementedError

    def delete_many(self, ids: List[int]) -> int:
        """Supprimer plusieurs books du dépôt par leurs identifiants uniques.

        Args:
            ids (List[int]): La liste des identifiants uniques des books à supprimer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de books supprimés.
        """
        raise NotImplementedError

    def delete(self, id: int) -> bool:
        """Supprimer un book du dépôt par son identifiant unique.

        Args:
            id (int): L'identifiant unique du book à supprimer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book a été supprimé avec succès, False sinon.
        """
        raise NotImplementedError
