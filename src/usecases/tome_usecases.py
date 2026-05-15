import re
from pathlib import Path
from typing import Tuple

from bs4 import BeautifulSoup

from domain import Tome
from ports import (
    LoggerInterface,
    TomeRepositoryInterface,
)

from .list_of_books_usecases import ListOfBooksUseCases


class TomeUseCases:
    Url_of_list_of_books: str = (
        "https://www.bibliotheque-des-aventuriers.com/menu/4_serie/loup_solitaire.htm"
    )

    def __init__(
        self,
        repo: TomeRepositoryInterface,
        logger: LoggerInterface,
        list_of_book_usecases: ListOfBooksUseCases,
    ):
        self.__repo = repo
        self.__logger: LoggerInterface = logger
        self.__list_of_book_usecases = list_of_book_usecases

    # region CRUD
    def update(self, tome: Tome) -> bool:
        return self.__repo.update(tome)

    def get(self, numero: int) -> Tome:
        return self.__repo.get(numero)

    def find(self, numero: int) -> Tome | None:
        return self.__repo.find(numero)

    def list(self) -> list[Tome]:
        return self.__repo.list()

    # endregion

    def download_list_of_books_from_url(self) -> list[Tome]:
        results: list[Tome] = []
        html_contents = self.__list_of_book_usecases.load()
        exceptions: list[Exception] = []
        self.__logger.info(
            "Finding data for each book from html contents", self.__class__.__name__
        )
        for content in html_contents:
            try:
                soup = BeautifulSoup(content.text, "html.parser")
                numero = int(Path(content.url).name.split("_", 1)[0])
                titre_from_html = soup.select_one(
                    "table#AutoNumber1 p:nth-child(1)"
                ).get_text(strip=True)
                titre = re.sub(
                    r"\(.*\)|Voir.*$", "", titre_from_html, flags=re.DOTALL
                )  # retire les parenthèses et le texte "Voir..." qui suit, présent dans les titres du premier tome qui a 2 versions: "classique" et "augmentée"
                titre = re.sub(
                    r"\s+", " ", titre
                ).strip()  # gère \r\n\t et doubles espaces

                titre_original: str = soup.select_one(
                    "table#AutoNumber2 tr:nth-child(2) td:nth-child(2) i"
                ).get_text(strip=True)

                description: str = soup.select_one(
                    "table#AutoNumber2 tr:nth-child(3) td p:nth-child(5)"
                ).get_text(strip=True)
                description = re.sub(r"\s+", " ", description).strip()

                results.append(
                    Tome(
                        numero=numero,
                        titre=titre,
                        titre_original=titre_original,
                        description=description,
                    )
                )
                self.__logger.debug(
                    f"Parsed tome {numero}: '{titre}'", self.__class__.__name__
                )
            except Exception as e:
                self.__logger.error(
                    f"Error parsing tome from content name '{content.name}': {e}",
                    self.__class__.__name__,
                )
                exceptions.append(e)
                continue
        if len(exceptions) > 0:
            raise ValueError(
                f"Errors occurred during parsing: {len(exceptions)} errors. See logs for details."
            )
        add_count = self.__repo.add_many(results)
        if add_count != len(results):
            self.__logger.warning(
                "Not all tomes were added to the repository.", self.__class__.__name__
            )
            raise ValueError("Not all tomes were added to the repository.")

        # si tout va bien jusqu'ici, on va parser pour rechercher les noms et numérris des tomes
        # ensuite nous ferons une recherche en fonction du site pour obtenir les prix

        # il faudra certainement retirer les prix et les dates
        # ajouter un sous liste de prix/dates/source=amazon,etc pour chaque tome
        # pour le moment on fait kiss pour la persistance de données => direct dans un fichier json
        # pour l'hebergement on pensera donc à un volume pour l'instant sachant qu'il faudra trouver un chart helm pour la base de donnée qui reste à choisir => postgresql, tinydb, etc
        # raise NotImplementedError("Parsing logic not implemented yet")

        return results

    def get_total_and_average(self) -> Tuple[float, float]:
        self.__logger.info(
            "Calculating total and average prices", self.__class__.__name__
        )
        tomes = self.__repo.list()
        total = sum(t.prix for t in tomes)
        average = total / len(tomes) if tomes else 0.0
        return total, average
