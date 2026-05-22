"""Gateways: couche d'adaptateurs d'accès aux données (ports/adapters).

Dans la Clean Architecture, le répertoire `gateways` contient les adaptateurs
qui implémentent les interfaces demandées par le domaine/usecases pour
accéder aux données (base, fichiers, API externes, mémoire, etc.).

- TomeRepositoryInterface : définit le contrat attendu par les usecases.
- InMemoryTomeRepository : implémentation simple utile pour les tests ou
  pour des scénarios sans persistance externe.

Remarque : les usecases dépendent de l'interface (abstraction), pas de cette
implémentation concrète. On peut remplacer InMemoryTomeRepository par une
implémentation DB sans modifier le domaine.
"""

from json import dumps as json_dumps
from json import loads as json_loads
from typing import Any, List

from domain import Book
from ports import BookRepositoryInterface, FileSystemInterface, LoggerInterface


class BookFileRepository(BookRepositoryInterface):
    """Implémentation d'un dépôt de tomes basé sur le système de fichiers.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookRepositoryInterface (BookRepositoryInterface): Interface du dépôt de tomes.
    """

    def __init__(
        self,
        logger: LoggerInterface,
        fs: FileSystemInterface,
        connection_string: str,
    ):
        self.__logger: LoggerInterface = logger
        self.__fs: FileSystemInterface = fs
        self.__connection_string: str = connection_string
        if not self.__fs.is_file_exists(self.__connection_string):
            self.__fs.write_file(self.__connection_string, "{}")

    # region gestion des fichiers : extraction et persistance
    def __extract(self) -> dict[str, Book]:
        """Extrait les données des tomes depuis le système de fichiers.

        Returns:
            dict[str, Book]: Un dictionnaire de tomes extraits.
        """
        content = self.__fs.read_file(self.__connection_string, withLog=False)
        data: dict[str, Any] = json_loads(content)

        results = {key: Book(**item) for key, item in data.items()}
        self.__logger.debug(
            f"Extracted tomes from file system at {self.__connection_string} : {len(results) + 1} items",
            self.__class__.__name__,
        )
        return results

    def __persist(self, tomes: dict[str, Book]):
        """Persiste les données des tomes dans le système de fichiers.

        Args:
            tomes (dict[str, Book]): Un dictionnaire de tomes à persister.
        """
        data = {key: tome.model_dump(mode="json") for key, tome in tomes.items()}
        self.__fs.write_file(
            self.__connection_string, json_dumps(data, indent=2), withLog=False
        )
        self.__logger.debug(
            f"Persisted tomes to file system at {self.__connection_string} : {len(tomes) + 1} items",
            self.__class__.__name__,
        )

    # endregion

    def list(self) -> List[Book]:
        """Liste tous les tomes.

        Returns:
            List[Book]: Une liste de tous les tomes.
        """
        try:
            data: dict[str, Book] = self.__extract()
            self.__logger.info(
                f"Listed {len(data)} tomes from file system at {self.__connection_string}",
                self.__class__.__name__,
            )
            return list(data.values())
        except Exception as e:
            self.__logger.error(f"Error listing tomes: {e}", self.__class__.__name__)
        return []

    def add_many(self, tomes: List[Book]) -> int:
        """Ajoute plusieurs tomes au dépôt.

        Args:
            tomes (List[Book]): La liste des tomes à ajouter.

        Returns:
            int: Le nombre de tomes ajoutés.
        """
        try:
            data: dict[str, Book] = self.__extract()
            for tome in tomes:
                data[str(tome.numero)] = tome

            self.__persist(data)
            self.__logger.info(
                f"Added {len(tomes)} tomes to file system at {self.__connection_string}",
                self.__class__.__name__,
            )
            return len(tomes)
        except Exception as e:
            self.__logger.error(f"Error adding tomes: {e}", self.__class__.__name__)

        return 0

    def add(self, tome: Book) -> bool:
        """Ajoute un tome au dépôt.

        Args:
            tome (Book): Le tome à ajouter.

        Returns:
            bool: True si le tome a été ajouté avec succès, False sinon.
        """
        try:
            data: dict[str, Book] = self.__extract()
            data[str(tome.numero)] = tome
            self.__persist(data)
            self.__logger.info(
                f"Added tome {tome.numero} to file system at {self.__connection_string}",
                self.__class__.__name__,
            )
            return True
        except Exception as e:
            self.__logger.error(
                f"Error adding tome {tome.numero}: {e}", self.__class__.__name__
            )
        return False

    def get(self, numero: int) -> Book:
        """Récupère un tome par son numéro.

        Args:
            numero (int): Le numéro du tome à récupérer.

        Raises:
            ValueError: Si le tome n'est pas trouvé.

        Returns:
            Book: Le tome correspondant au numéro.
        """
        data = self.find(numero)
        if not data:
            raise ValueError(f"Tome with numero {numero} not found.")
        return data

    def find(self, numero: int) -> Book | None:
        """Récupère un tome par son numéro.

        Args:
            numero (int): Le numéro du tome à récupérer.

        Returns:
            Book | None: Le tome correspondant au numéro ou None s'il n'est pas trouvé.
        """
        try:
            data: dict[str, Book] = self.__extract()
            item = data.get(str(numero), None)
            if item is not None:
                self.__logger.info(
                    f"Got tome {item.numero} from file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
                return item
            else:
                self.__logger.info(
                    f"Tome {numero} not found in file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
        except Exception as e:
            self.__logger.error(
                f"Error getting tome {numero}: {e}", self.__class__.__name__
            )
        return None

    def update(self, tome: Book) -> bool:
        """Met à jour un tome dans le dépôt.

        Args:
            tome (Book): Le tome à mettre à jour.

        Returns:
            bool: True si le tome a été mis à jour avec succès, False sinon.
        """
        try:
            data: dict[str, Book] = self.__extract()
            if str(tome.numero) in data:
                data[str(tome.numero)] = tome
                self.__persist(data)
                self.__logger.info(
                    f"Updated tome {tome.numero} in file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
                return True
            else:
                self.__logger.warning(
                    f"Tome {tome.numero} not found in file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
        except Exception as e:
            self.__logger.error(
                f"Error updating tome {tome.numero}: {e}", self.__class__.__name__
            )
        return False

    def delete(self, numero: int) -> bool:
        """Supprime un tome du dépôt.

        Args:
            numero (int): Le numéro du tome à supprimer.

        Returns:
            bool: True si le tome a été supprimé avec succès, False sinon.
        """
        try:
            data: dict[str, Book] = self.__extract()
            if str(numero) in data:
                del data[str(numero)]
                self.__persist(data)
                self.__logger.info(
                    f"Removed tome {numero} from file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
                return True
            else:
                self.__logger.warning(
                    f"Tome {numero} not found in file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
        except Exception as e:
            self.__logger.error(
                f"Error removing tome {numero}: {e}", self.__class__.__name__
            )
        return False
