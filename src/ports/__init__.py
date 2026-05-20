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

from ports.file_system import FileSystemInterface
from ports.html_reader import HTMLReaderInterface
from ports.logger import LoggerInterface
from ports.tome_repository import TomeRepositoryInterface

__all__ = [
    "TomeRepositoryInterface",
    "LoggerInterface",
    "FileSystemInterface",
    "HTMLReaderInterface",
]
