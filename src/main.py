import os
from pathlib import Path

from dotenv import load_dotenv

from gateways import (
    FileSystemAdapter,
    HTMLReaderAdapter,
    LoggerAdapter,
    TomeFileRepository,
)
from usecases import ListOfBooksUseCases, TomeUseCases

SCRIPT_ROOT_DIR = Path(__file__).parent

# arrange
_env = os.getenv("ENV", "dev")
if _env == "dev":
    # charge les variables du fichier .env si le fichier est présent sinon récupération depuis les variable d'environnement
    load_dotenv()


env = {
    "CONNECTION_STRING": os.getenv("CONNECTION_STRING", None),
    "ENV": _env,
    "LOG_FILE": os.getenv("LOG_FILE", None),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "WARN"),
}
env["FILE_SYSTEM_PATH"] = os.getenv(
    "FILE_SYSTEM_PATH",
    str(SCRIPT_ROOT_DIR / "data")
    if env["ENV"] != "dev"
    else str(SCRIPT_ROOT_DIR.parent / "data"),
)

logger = LoggerAdapter(log_file=env["LOG_FILE"], log_level=env["LOG_LEVEL"])
logger.info(
    f"--------------------  Starting application [{__file__}]   ------------------"
)
logger.debug(
    "--------------------          initialization              ------------------"
)
logger.debug("environment variables:")
for key, value in env.items():
    logger.debug(f"  {key} = {value}", "INIT")

# IOC simulation
# on instancie les adaptateurs (implémentations concrètes) et on les injecte dans les usecases.
# Les usecases ne connaissent que les interfaces (abstractions) et restent découplés des implémentations concrètes.
adapters = {}
adapters["logger"] = logger
adapters["fs"] = FileSystemAdapter(
    logger=adapters["logger"], path=env["FILE_SYSTEM_PATH"]
)
adapters["html_reader"] = HTMLReaderAdapter(logger=adapters["logger"])
logger.debug("adapters finalized", "INIT")

repositories = {}
repositories["tome"] = TomeFileRepository(
    logger=adapters["logger"],
    fs=adapters["fs"],
    connection_string=env["CONNECTION_STRING"],
)
logger.debug("repositories finalized", "INIT")

# arrange
list_of_books_usecases = ListOfBooksUseCases(
    html_reader=adapters["html_reader"], fs=adapters["fs"], logger=adapters["logger"]
)
tome_use_cases = TomeUseCases(
    repositories["tome"], adapters["logger"], list_of_books_usecases
)
logger.debug("usecases finalized", "INIT")

# action
tomes = tome_use_cases.download_list_of_books_from_url()

if env["ENV"] == "dev":
    adapters["logger"].info("")
    for tome in tomes:
        adapters["logger"].info(
            f" - {tome.numero}: '{tome.titre}',  Description: {tome.description[:50]}...",
            "DEV ONLY",
        )
