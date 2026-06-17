import asyncio
import logging
from pathlib import Path

from ioc import new_ioc_container, print_environment_variables


async def main():
    # load dependencies

    container = new_ioc_container(script_name=Path(__file__).stem)

    logger = logging.getLogger(__name__)
    logger.info("IOC container initialized")

    print_environment_variables(container, logger)

    # arrange
    book_list_usecases = container.book_list_usecases()

    # action
    async with container.unit_of_work():
        books = await book_list_usecases.fetch_books()

    # pour le moment on fait kiss pour la persistance de données => direct dans un fichier json
    # pour l'hebergement on pensera donc à un volume pour l'instant sachant qu'il faudra trouver un chart helm pour la base de donnée qui reste à choisir => postgresql, tinydb, etc

    logger.info("")
    logger.info("summary:")
    sorted_book = sorted(books, key=lambda b: b.numero)
    for book in sorted_book:
        logger.info(f" - {book}")


if __name__ == "__main__":
    asyncio.run(main())
