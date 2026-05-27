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

    def add_many(self, books: List[Book]) -> int:
        """Ajouter plusieurs books au dépôt.

        Args:
            books (List[Book]): La liste des books à ajouter.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            int: Le nombre de books ajoutés.
        """
        raise NotImplementedError

    def add(self, book: Book) -> bool:
        """Ajouter un book au dépôt.

        Args:
            book (Book): Le book à ajouter.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book a été ajouté, False sinon.
        """
        raise NotImplementedError

    def get(self, id: int) -> Book:
        """Récupérer un book par son numéro.

        Args:
            numero (int): Le numéro du book à récupérer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            Book: Le book correspondant au numéro.
        """
        raise NotImplementedError

    def find(self, id: int) -> Book | None:
        """Trouver un book par son numéro.

        Args:
            numero (int): Le numéro du book à trouver.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            Book | None: Le book correspondant au numéro, ou None s'il n'existe pas.
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

    def delete(self, numero: int) -> bool:
        """Supprimer un book du dépôt par son numéro.

        Args:
            numero (int): Le numéro du book à supprimer.

        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée.

        Returns:
            bool: True si le book a été supprimé avec succès, False sinon.
        """
        raise NotImplementedError
