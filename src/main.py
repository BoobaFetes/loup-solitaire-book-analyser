import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from adapters import (
    BookFileRepository,
    FileSystemAdapter,
    HTMLReaderAdapter,
    LoggerAdapter,
)
from usecases import BookUseCases, MainUseCases

SCRIPT_ROOT_DIR = Path(__file__).parent

# arrange
_env = os.getenv("ENV", "dev")
if _env == "dev":
    # charge les variables du fichier .env si le fichier est présent sinon récupération depuis les variable d'environnement
    load_dotenv()


env: dict[str, str] = {
    "CONNECTION_STRING": os.getenv("CONNECTION_STRING", ""),
    "ENV": _env,
    "LOG_FILE": os.getenv("LOG_FILE", ""),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "WARN"),
}
env["FILE_SYSTEM_PATH"] = os.getenv(
    "FILE_SYSTEM_PATH",
    str(SCRIPT_ROOT_DIR / "data")
    if env["ENV"] != "dev"
    else str(SCRIPT_ROOT_DIR.parent / "data"),
)

logger = LoggerAdapter(log_file=env["LOG_FILE"], log_level=env["LOG_LEVEL"])
logger.debug(
    f"--------------------  application [{__file__}] starts   ------------------"
)

logger.debug("environment variables:")
for key, value in env.items():
    logger.debug(f"  {key} = {value}", "INIT")

# IOC simulation
# on instancie les adaptateurs (implémentations concrètes) et on les injecte dans les usecases.
# Les usecases ne connaissent que les interfaces (abstractions) et restent découplés des implémentations concrètes.
fs = FileSystemAdapter(logger, path=env["FILE_SYSTEM_PATH"])
html_reader = HTMLReaderAdapter(logger=logger)
logger.debug("adapters finalized", "INIT")

repositories = {}
repositories["tome"] = BookFileRepository(
    logger,
    fs,
    connection_string=env["CONNECTION_STRING"],
)
logger.debug("repositories finalized", "INIT")

# arrange
book_usecases = BookUseCases(html_reader, logger)
main_usecases = MainUseCases(book_usecases, repositories["tome"], logger)
logger.debug("usecases finalized", "INIT")


# action
async def main():
    tomes = await main_usecases.download_tomes()
    # si tout va bien jusqu'ici, on va parser pour rechercher les noms et numérris des tomes
    # ensuite nous ferons une recherche en fonction du site pour obtenir les prix

    # il faudra certainement retirer les prix et les dates
    # ajouter un sous liste de prix/dates/source=amazon,etc pour chaque tome
    # pour le moment on fait kiss pour la persistance de données => direct dans un fichier json
    # pour l'hebergement on pensera donc à un volume pour l'instant sachant qu'il faudra trouver un chart helm pour la base de donnée qui reste à choisir => postgresql, tinydb, etc
    # raise NotImplementedError("Parsing logic not implemented yet")

    if env["ENV"] == "dev":
        logger.info("")
        for tome in tomes:
            logger.info(
                f" - {tome.numero}: '{tome.titre}',  Description: {tome.description[:50]}...",
                "DEV ONLY",
            )


asyncio.run(main())
logger.debug(
    f"--------------------  application [{__file__}] ends   ------------------"
)