# import asyncio
# from pathlib import Path

# from adapters import (
#     BookFileRepository,
#     EnvironmentAdapter,
#     FileSystemAdapter,
#     LoggerAdapter,
# )
# from domain import Book
# from usecases import BookUseCases

# SCRIPT_ROOT_DIR = Path(__file__).parent

# # arrange
# env = EnvironmentAdapter()
# env.init(SCRIPT_ROOT_DIR)

# logger = LoggerAdapter(log_file=env.get("LOG_FILE"), log_level=env.get("LOG_LEVEL"))

# logger.info("environment variables:", "INIT")
# for key, value in env.items():
#     logger.info(f" - {key} = {value}", "INIT")

# # IOC simulation
# # on instancie les adaptateurs (implémentations concrètes) et on les injecte dans les usecases.
# # Les usecases ne connaissent que les interfaces (abstractions) et restent découplés des implémentations concrètes.
# fs = FileSystemAdapter(logger, path=env.get("FILE_SYSTEM_PATH"))
# book_repository = BookFileRepository(
#     logger,
#     fs,
#     connection_string=env.get("CONNECTION_STRING"),
# )
# logger.info("IOC : common instances (singleton) created", "INIT")

# # arrange
# book_usecases = BookUseCases(book_repository, logger)
# logger.info("usecases created", "INIT")


# # action
# async def main():
#     # TODO : MERGE des données depuis l'ancienne version du projet pour récupérer les numéros de tome manquants
#     # avec galllimart jeunesse il ya  des trous dans les numéros de tome
#     # il va falloir faire un merge des informations depuis l'ancienne version du projet pour récupérer les numéros de tome manquants
#     # depuis l'ancienne version du projet on a le numéro et le nom d'un tome mais pas les prix et les dates de sortie
#     books: list[Book] = await book_usecases.fetch_books()

#     # si tout va bien jusqu'ici, on va parser pour rechercher les noms et numérris des tomes
#     # ensuite nous ferons une recherche en fonction du site pour obtenir les prix

#     # il faudra certainement retirer les prix et les dates
#     # ajouter un sous liste de prix/dates/source=amazon,etc pour chaque tome
#     # pour le moment on fait kiss pour la persistance de données => direct dans un fichier json
#     # pour l'hebergement on pensera donc à un volume pour l'instant sachant qu'il faudra trouver un chart helm pour la base de donnée qui reste à choisir => postgresql, tinydb, etc
#     # raise NotImplementedError("Parsing logic not implemented yet")

#     if env.get("ENV") == "dev":
#         logger.info("")
#         sorted_book = sorted(books, key=lambda b: b.numero)
#         for book in sorted_book:
#             logger.info(
#                 f" - {book}",
#                 "DEV ONLY",
#             )


# asyncio.run(main())
