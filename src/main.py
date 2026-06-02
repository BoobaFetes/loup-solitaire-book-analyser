import asyncio
import logging

from domain import Book
from ioc import new_ioc_container, print_environment_variables

# load dependencies
container = new_ioc_container()

logger = logging.getLogger(__name__)
logger.info("IOC container initialized")

print_environment_variables(container, logger)

logger.info("IOC : common instances (singleton) created")

# arrange
book_usecases = container.book_usecases()


# action
async def main():
    # TODO : MERGE des données depuis l'ancienne version du projet pour récupérer les numéros de tome manquants
    # avec galllimart jeunesse il ya  des trous dans les numéros de tome
    # il va falloir faire un merge des informations depuis l'ancienne version du projet pour récupérer les numéros de tome manquants
    # depuis l'ancienne version du projet on a le numéro et le nom d'un tome mais pas les prix et les dates de sortie
    books: list[Book] = await book_usecases.fetch_books()

    # si tout va bien jusqu'ici, on va parser pour rechercher les noms et numérris des tomes
    # ensuite nous ferons une recherche en fonction du site pour obtenir les prix

    # il faudra certainement retirer les prix et les dates
    # ajouter un sous liste de prix/dates/source=amazon,etc pour chaque tome
    # pour le moment on fait kiss pour la persistance de données => direct dans un fichier json
    # pour l'hebergement on pensera donc à un volume pour l'instant sachant qu'il faudra trouver un chart helm pour la base de donnée qui reste à choisir => postgresql, tinydb, etc
    # raise NotImplementedError("Parsing logic not implemented yet")

    logger.info("")
    logger.info("summary:")
    sorted_book = sorted(books, key=lambda b: b.numero)
    for book in sorted_book:
        logger.info(f" - {book}")


asyncio.run(main())
