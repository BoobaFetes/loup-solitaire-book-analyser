from typing import List

from domain import Tome


class TomeRepositoryInterface:
    """Contrat (port) pour un dépôt de Tome.

    Les usecases appelleront ces méthodes sans connaître l'implémentation.
    """

    def list(self) -> List[Tome]:
        """Retourner la liste de tous les tomes."""
        raise NotImplementedError

    def add_many(self, tomes: List[Tome]) -> int:
        """Ajouter plusieurs tomes au dépôt."""
        raise NotImplementedError

    def add(self, tome: Tome) -> bool:
        """Ajouter un tome au dépôt."""
        raise NotImplementedError

    def get(self, numero: int) -> Tome:
        """Récupérer un tome par son numéro."""
        raise NotImplementedError

    def find(self, numero: int) -> Tome | None:
        """Récupérer un tome par son numéro."""
        raise NotImplementedError

    def update(self, tome: Tome) -> bool:
        """Mettre à jour un tome existant dans le dépôt."""
        raise NotImplementedError

    def delete(self, numero: int) -> bool:
        """Supprimer un tome du dépôt par son numéro."""
        raise NotImplementedError
