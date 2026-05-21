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
from typing import List

from domain import Book
from ports import BookRepositoryInterface, FileSystemInterface, LoggerInterface


class BookFileRepository(BookRepositoryInterface):
    """Implémentation en mémoire du dépôt de tomes.

    Utile pour :
    - tests unitaires rapides,
    - prototypes sans persistance,
    - ou comme stub en développement.
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
        content = self.__fs.read_file(self.__connection_string, withLog=False)
        data: dict[str, dict] = json_loads(content)
        return {key: Book(**item) for key, item in data.items()}

    def __persist(self, tomes: dict[str, Book]):
        data = {key: tome.model_dump(mode="json") for key, tome in tomes.items()}
        self.__fs.write_file(
            self.__connection_string, json_dumps(data, indent=2), withLog=False
        )

    # endregion

    def list(self) -> List[Book]:
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
        data = self.find(numero)
        if not data:
            raise ValueError(f"Tome with numero {numero} not found.")
        return data

    def find(self, numero: int) -> Book | None:
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
                self.__logger.info(
                    f"Tome {tome.numero} not found in file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
        except Exception as e:
            self.__logger.error(
                f"Error updating tome {tome.numero}: {e}", self.__class__.__name__
            )
        return False

    def delete(self, numero: int) -> bool:
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
                self.__logger.info(
                    f"Tome {numero} not found in file system at {self.__connection_string}",
                    self.__class__.__name__,
                )
        except Exception as e:
            self.__logger.error(
                f"Error removing tome {numero}: {e}", self.__class__.__name__
            )
        return False
