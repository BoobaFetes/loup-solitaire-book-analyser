"""Gateways: couche d'adaptateurs d'accès aux données (ports/adapters).

Dans la Clean Architecture, le répertoire `gateways` contient les adaptateurs
qui implémentent les interfaces demandées par le domaine/usecases pour
accéder aux données (base, fichiers, API externes, mémoire, etc.).

- BookRepositoryInterface : définit le contrat attendu par les usecases.
- BookFileRepository : implémentation simple utile pour les tests ou
  pour des scénarios sans persistance externe.

Remarque : les usecases dépendent de l'interface (abstraction), pas de cette
implémentation concrète. On peut remplacer BookFileRepository par une
implémentation DB sans modifier le domaine.
"""

import logging
from json import dumps as json_dumps
from json import loads as json_loads
from typing import Any, List

from domain import Book
from ports import BookRepositoryInterface, FileSystemInterface


class BookFileRepository(BookRepositoryInterface):
    """Implémentation d'un dépôt de books basé sur le système de fichiers.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookRepositoryInterface (BookRepositoryInterface): Interface du dépôt de books.
    """

    def __init__(
        self,
        fs: FileSystemInterface,
        connection_string: str,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._fs: FileSystemInterface = fs
        self._connection_string: str = connection_string
        if not self._fs.is_file_exists(self._connection_string):
            self._fs.write_file(self._connection_string, "{}")

    # region gestion des fichiers : extraction et persistance
    def __extract(self) -> dict[str, Book]:
        """Extrait les données des books depuis le système de fichiers.

        Returns:
            dict[str, Book]: Un dictionnaire de books extraits.
        """
        content = self._fs.read_file(self._connection_string, withLog=False)
        data: dict[str, Any] = json_loads(content)

        results = {key: Book(**item) for key, item in data.items()}
        self._logger.info(
            f"Extracted books from file system at {self._connection_string} : {len(results) + 1} items",
        )
        return results

    def __persist(self, books: dict[str, Book]):
        """Persiste les données des books dans le système de fichiers.

        Args:
            books (dict[str, Book]): Un dictionnaire de books à persister.
        """
        data = {key: book.model_dump(mode="json") for key, book in books.items()}
        self._fs.write_file(
            self._connection_string, json_dumps(data, indent=2), withLog=False
        )
        self._logger.info(
            f"Persisted books to file system at {self._connection_string} : {len(books) + 1} items",
        )

    # endregion

    def clear(self) -> bool:
        """Efface tous les books du dépôt.

        Returns:
            bool: True si le dépôt a été vidé avec succès, False sinon.
        """
        try:
            self._fs.write_file(self._connection_string, "{}")
            self._logger.info(
                f"Cleared all books from file system at {self._connection_string}",
            )
            return True
        except Exception as e:
            self._logger.error(f"Error clearing books: {e}")
        return False

    def list(self) -> List[Book]:
        """Liste tous les books.

        Returns:
            List[Book]: Une liste de tous les books.
        """
        try:
            data: dict[str, Book] = self.__extract()
            self._logger.info(
                f"Listed {len(data)} books from file system at {self._connection_string}",
            )
            return list(data.values())
        except Exception as e:
            self._logger.error(f"Error listing books: {e}")
        return []

    def add_many(self, books: List[Book]) -> int:
        """Ajoute plusieurs books au dépôt.

        Args:
            books (List[Book]): La liste des books à ajouter.

        Returns:
            int: Le nombre de books ajoutés.
        """
        try:
            data: dict[str, Book] = self.__extract()
            for book in books:
                data[str(book.id)] = book

            count = len(data.keys())
            self.__persist(data)
            self._logger.info(
                f"Added {count} books to file system at {self._connection_string}",
            )
            return count
        except Exception as e:
            self._logger.error(f"Error adding books: {e}")

        return 0

    def add(self, book: Book) -> bool:
        """Ajoute un book au dépôt.

        Args:
            book (Book): Le book à ajouter.

        Returns:
            bool: True si le book a été ajouté avec succès, False sinon.
        """
        try:
            data: dict[str, Book] = self.__extract()
            data[str(book.numero)] = book
            self.__persist(data)
            self._logger.info(
                f"Added book {book.numero} to file system at {self._connection_string}",
            )
            return True
        except Exception as e:
            self._logger.error(f"Error adding book {book.numero}: {e}")
        return False

    def get(self, id: int) -> Book:
        """Récupère un book par son numéro.

        Args:
            id (int): L'identifiant du book à récupérer.

        Raises:
            ValueError: Si le book n'est pas trouvé.

        Returns:
            Book: Le book correspondant au numéro.
        """
        data = self.find(id)
        if not data:
            raise ValueError(f"book with id {id} not found.")
        return data

    def find(self, id: int) -> Book | None:
        """Récupère un book par son numéro.

        Args:
            id (int): L'identifiant du book à récupérer.

        Returns:
            Book | None: Le book correspondant au numéro ou None s'il n'est pas trouvé.
        """
        try:
            data: dict[str, Book] = self.__extract()
            item = data.get(str(id), None)
            if item is not None:
                self._logger.info(
                    f"Got book {item.id} from file system at {self._connection_string}",
                )
                return item
            else:
                self._logger.info(
                    f"book id:{id} not found in file system at {self._connection_string}",
                )
        except Exception as e:
            self._logger.error(f"Error getting book {id}: {e}")
        return None

    def update(self, book: Book) -> bool:
        """Met à jour un book dans le dépôt.

        Args:
            book (Book): Le book à mettre à jour.

        Returns:
            bool: True si le book a été mis à jour avec succès, False sinon.
        """
        try:
            data: dict[str, Book] = self.__extract()
            if str(book.numero) in data:
                data[str(book.numero)] = book
                self.__persist(data)
                self._logger.info(
                    f"Updated book {book.numero} in file system at {self._connection_string}",
                )
                return True
            else:
                self._logger.warning(
                    f"book {book.numero} not found in file system at {self._connection_string}",
                )
        except Exception as e:
            self._logger.error(f"Error updating book {book.numero}: {e}")
        return False

    def delete(self, numero: int) -> bool:
        """Supprime un book du dépôt.

        Args:
            numero (int): Le numéro du book à supprimer.

        Returns:
            bool: True si le book a été supprimé avec succès, False sinon.
        """
        try:
            data: dict[str, Book] = self.__extract()
            if str(numero) in data:
                del data[str(numero)]
                self.__persist(data)
                self._logger.info(
                    f"Removed book {numero} from file system at {self._connection_string}",
                )
                return True
            else:
                self._logger.warning(
                    f"book {numero} not found in file system at {self._connection_string}",
                )
        except Exception as e:
            self._logger.error(f"Error removing book {numero}: {e}")
        return False
