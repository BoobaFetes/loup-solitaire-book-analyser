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
from typing import Any, List, Literal
from urllib.parse import urljoin

from domain import BookPrice
from ports import BookPriceRepositoryInterface, FileSystemInterface


class BookPriceFileRepository(BookPriceRepositoryInterface):
    """Implémentation d'un dépôt de book prices basé sur le système de fichiers.

    Utile pour :
        - tests unitaires rapides,
        - prototypes sans persistance,
        - ou comme stub en développement.
    Args:
        BookPriceRepositoryInterface (BookPriceRepositoryInterface): Interface du dépôt de book prices.
    """

    def __init__(
        self,
        fs: FileSystemInterface,
        connection_string: str,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._fs: FileSystemInterface = fs
        self._connection_string: str = urljoin(connection_string, "prices.data.json")
        if not self._fs.is_file_exists(self._connection_string):
            self._fs.write_file(self._connection_string, "{}")

    # region gestion des fichiers : extraction et persistance
    def __extract(self) -> dict[str, list[BookPrice]]:
        """Extrait les données des book prices depuis le système de fichiers.

        Returns:
            dict[str, list[BookPrice]]: Un dictionnaire de book prices dont les clés sont les ISBN.
        Notes:
        La structure de données retournée est la suivante :
        ```
        {
            "isbn1": [BookPrice(...), BookPrice(...), ...],
            "isbn2": [BookPrice(...), BookPrice(...), ...],
            ...
        }
        ```
        """
        content = self._fs.read_file(self._connection_string)
        data: dict[str, Any] = json_loads(content)

        results = {
            key: [BookPrice(**item) for item in items] for key, items in data.items()
        }
        self._logger.info(
            f"Extracted book prices from file system at {self._connection_string} : {len(results) + 1} items",
        )
        return results

    def __persist(self, prices: dict[str, list[BookPrice]]):
        """Persiste les données des book prices dans le système de fichiers.

        Args:
            prices (dict[str, list[BookPrice]]): Un dictionnaire de book prices à persister.
        """
        data = {
            key: [item.model_dump(mode="json") for item in items]
            for key, items in prices.items()
        }
        self._fs.write_file(self._connection_string, json_dumps(data, indent=2))
        self._logger.info(
            f"Persisted book prices to file system at {self._connection_string} : {len(prices)} items",
        )

    # endregion

    def clear(self) -> bool:
        """Efface tous les book prices du dépôt.

        Returns:
            bool: True si le dépôt a été vidé avec succès, False sinon.
        """
        try:
            self._fs.write_file(self._connection_string, "{}")
            self._logger.info(
                f"Cleared all book prices from file system at {self._connection_string}",
            )
            return True
        except Exception as e:
            self._logger.error(
                f"Error clearing book prices: {type(e).__name__}: {e}", exc_info=True
            )
        return False

    def list_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        data = self.__extract()
        if not isbns:
            return data
        return {isbn: data.get(isbn, []) for isbn in isbns}

    def list(self, isbn: str) -> List[BookPrice]:
        """Retourner la liste de tous les book prices pour un ISBN donné.

        Raises:
            Exception: Si une erreur se produit lors de la récupération des book prices.

        Returns:
            List[BookPrice]: La liste de tous les book prices.
        """
        try:
            data: list[BookPrice] = self.__extract().get(isbn, [])
            self._logger.info(
                f"Listed {len(data)} book prices for ISBN {isbn} from file system at {self._connection_string}",
            )
            return data
        except Exception as e:
            self._logger.error(
                f"Error listing book prices for ISBN {isbn}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return []

    def get(self, isbn: str, source: str, date: str | None = None) -> BookPrice:
        """Récupère un book price par son ISBN, sa source et éventuellement sa date.

        Args:
            isbn (str): L'ISBN du book price à récupérer.
            source (str): La source du book price à récupérer.
            date (str|None): La date du book price à récupérer (optionnelle).

        Raises:
            ValueError: Si le book n'est pas trouvé.

        Returns:
            BookPrice: Le book price correspondant à l'ISBN, à la source et à la date si fournis sinon le dernier.
        """
        data = self.find(isbn, source, date)
        if not data:
            raise ValueError(
                f"book price with ISBN {isbn} and source {source} not found."
            )
        return data

    def find(self, isbn: str, source: str, date: str | None = None) -> BookPrice | None:
        """Trouver un book price par son ISBN, sa source et éventuellement sa date.

        Args:
            isbn (str): L'ISBN du book price à trouver.
            source (str): La source du book price à trouver.
            date (str|None): La date du book price à trouver (optionnelle).

        Raises:
            Exception: Si une erreur se produit lors de la recherche du book.

        Returns:
            Book | None: Le book correspondant à l'identifiant, ou None s'il n'existe pas.
        """
        try:
            data = self.__extract()
            stored_data = data.get(isbn, [])
            for price in stored_data:
                if price.source == source and (date is None or price.date == date):
                    return price
            return None
        except Exception as e:
            self._logger.error(
                f"Error getting book price for ISBN {isbn}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return None

    def _keys_matches(
        self,
        price: BookPrice,
        stored_price: BookPrice,
        for_operation: Literal["add", "update", "delete"],
    ) -> bool:

        # s'il ne s'agit pas du tout de la meme source et du meme isbn alors ce n'est pas le même item
        if not (
            price.isbn == stored_price.isbn and price.source == stored_price.source
        ):
            return False

        if for_operation in ["update", "delete"]:
            # si la date doit matcher alors on vérifie que c'est le même item en comparant la date
            # dans le cas d'une mise à jour ou d'une suppression les 3 clés doivent matcher
            return price.date == stored_price.date
        elif for_operation == "add":
            # dans le cas d'un ajout, la date ne doit pas matcher
            return True
        else:
            # vu que l'on utilise pyright pour valider les types, cette condition ne devrait jamais être vérifiée, mais on la laisse pour garantir la robustesse du code en cas de mauvaise utilisation de la méthode
            raise ValueError(
                f"Invalid operation: {for_operation}. Expected 'add', 'update' or 'delete'."
            )

    def add_many(self, prices: List[BookPrice]) -> int:
        """Ajouter plusieurs book prices au dépôt.

        Args:
            prices (List[BookPrice]): La liste des book prices à ajouter.

        Raises:
            Exception: Si une erreur se produit lors de l'ajout des book prices.

        Returns:
            int: Le nombre de book prices ajoutés.
        """
        try:
            data = self.__extract()

            count = 0
            for price in prices:
                stored_data = data.get(price.isbn, [])
                data[price.isbn] = stored_data

                if any(
                    [
                        data
                        for data in stored_data
                        if self._keys_matches(price, data, for_operation="add")
                    ]
                ):
                    continue

                stored_data.append(price)
                count += 1

            self.__persist(data)
            self._logger.info(
                f"Added {count} book prices to file system at {self._connection_string}",
            )
            return count
        except Exception as e:
            self._logger.error(
                f"Error adding book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    def add(self, price: BookPrice) -> bool:
        """Ajoute un book price au dépôt.

        Args:
            price (BookPrice): Le book price à ajouter.

        Raises:
            Exception: Si une erreur se produit lors de l'ajout du book price.

        Returns:
            bool: True si le book price a été ajouté avec succès, False sinon.
        """
        try:
            data = self.__extract()
            stored_data = data.get(price.isbn, [])
            data[price.isbn] = stored_data

            if any(
                [
                    data
                    for data in stored_data
                    if self._keys_matches(price, data, for_operation="add")
                ]
            ):
                return False

            stored_data.append(price)
            self.__persist(data)
            self._logger.info(
                f"Added book price for ISBN {price.isbn} with source {price.source} and price {price.prix} {price.currency} to file system at {self._connection_string}",
            )
            return True
        except Exception as e:
            self._logger.error(
                f"Error adding book price for ISBN {price.isbn}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return False

    def update_many(self, prices: List[BookPrice]) -> int:
        """Mettre à jour plusieurs book prices dans le dépôt.

        Args:
            prices (List[BookPrice]): La liste des book prices à mettre à jour.

        Raises:
            Exception: Si une erreur se produit lors de la mise à jour des book prices.

        Returns:
            int: Le nombre de book prices mis à jour.
        """
        try:
            data = self.__extract()

            count = 0
            for price in prices:
                stored_data = data.get(price.isbn, [])
                data[price.isbn] = stored_data

                for i, stored_price in enumerate(stored_data):
                    if self._keys_matches(price, stored_price, for_operation="update"):
                        stored_data[i] = price
                        count += 1
                        break

            self.__persist(data)
            self._logger.info(
                f"Updated {count} book prices in file system at {self._connection_string}",
            )
            return count
        except Exception as e:
            self._logger.error(
                f"Error updating book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return 0

    def update(self, price: BookPrice) -> bool:
        """Mettre à jour un book price existant dans le dépôt.

        Args:
            price (BookPrice): Le book price à mettre à jour.

        Raises:
            Exception: Si une erreur se produit lors de la mise à jour du book price.

        Returns:
            bool: True si le book price a été mis à jour avec succès, False sinon.
        """

        try:
            data = self.__extract()

            stored_data = data.get(price.isbn, [])
            data[price.isbn] = stored_data

            for i, stored_price in enumerate(stored_data):
                if self._keys_matches(price, stored_price, for_operation="update"):
                    stored_data[i] = price
                    break

            self.__persist(data)
            self._logger.info(
                f"Updated book price for ISBN {price.isbn} with source {price.source} and price {price.prix} {price.currency} in file system at {self._connection_string}",
            )
            return True
        except Exception as e:
            self._logger.error(
                f"Error updating book prices: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return False

    def delete_many(self, prices: List[BookPrice]) -> int:
        """Supprimer plusieurs books du dépôt par leurs identifiants uniques.

        Args:
            prices (List[BookPrice]): La liste des book prices à supprimer.

        Raises:
            Exception: Si une erreur se produit lors de la suppression des books.

        Returns:
            int: Le nombre de books supprimés.
        """
        try:
            data = self.__extract()

            count = 0
            for price in prices:
                stored_data = data.get(price.isbn, [])

                # On reconstruit la liste sans les éléments à supprimer
                new_list = [
                    p
                    for p in stored_data
                    if not self._keys_matches(p, price, for_operation="delete")
                ]

                removed = len(stored_data) - len(new_list)
                if removed > 0:
                    data[price.isbn] = new_list
                    count += removed

            if count > 0:
                self.__persist(data)
                self._logger.info(
                    f"Removed {count} book prices in file system at {self._connection_string}",
                )
            return count
        except Exception as e:
            self._logger.error(
                f"Error removing book {id}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return 0

    def delete(self, price: BookPrice) -> bool:
        """Supprimer un book du dépôt par son identifiant unique.

        Args:
            price (BookPrice): Le book price à supprimer.
            date (str): La date du book à supprimer.

        Raises:
            Exception: Si une erreur se produit lors de la suppression du book.

        Returns:
            bool: True si le book a été supprimé avec succès, False sinon.
        """
        try:
            data = self.__extract()
            stored_data = data.get(price.isbn, [])

            new_list = [
                p
                for p in stored_data
                if not self._keys_matches(p, price, for_operation="delete")
            ]

            removed = len(stored_data) - len(new_list)
            if removed > 0:
                data[price.isbn] = new_list
                self.__persist(data)
                self._logger.info(
                    f"Removed book price for ISBN {price.isbn} with source {price.source} and date {price.date} from file system at {self._connection_string}",
                )
                return True
        except Exception as e:
            self._logger.error(
                f"Error removing book {id}: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return False
