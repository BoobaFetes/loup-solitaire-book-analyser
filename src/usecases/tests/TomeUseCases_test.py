import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
from unittest.mock import MagicMock

from domain import Book
from usecases.main_usecases import MainUseCases


def make_tome(numero=1, prix=0.0):
    t = Book(
        numero=numero,
        titre=f"Tome {numero}",
        titre_original=f"Title {numero}",
        description="Desc",
    )
    t.prix = (
        prix  # prix n'est pas dans le modèle mais simulé ici pour get_total_and_average
    )
    return t


class TestTomeUseCases(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.logger = MagicMock()
        self.list_of_books_usecases = MagicMock()
        self.use_cases = MainUseCases(
            repo=self.repo,
            logger=self.logger,
            list_of_book_usecases=self.list_of_books_usecases,
        )

    def test_get_delegates_to_repo(self):
        tome = MagicMock()
        self.repo.get.return_value = tome
        result = self.use_cases.get(1)
        self.repo.get.assert_called_once_with(1)
        self.assertEqual(result, tome)

    def test_find_delegates_to_repo(self):
        self.repo.find.return_value = None
        result = self.use_cases.find(99)
        self.repo.find.assert_called_once_with(99)
        self.assertIsNone(result)

    def test_list_delegates_to_repo(self):
        self.repo.list.return_value = []
        result = self.use_cases.list()
        self.repo.list.assert_called_once()
        self.assertEqual(result, [])

    def test_update_delegates_to_repo(self):
        tome = MagicMock()
        self.repo.update.return_value = True
        result = self.use_cases.update(tome)
        self.repo.update.assert_called_once_with(tome)
        self.assertTrue(result)

    def test_get_total_and_average_empty(self):
        self.repo.list.return_value = []
        total, average = self.use_cases.get_total_and_average()
        self.assertEqual(total, 0.0)
        self.assertEqual(average, 0.0)

    def test_get_total_and_average_with_tomes(self):
        t1 = MagicMock()
        t1.prix = 10.0
        t2 = MagicMock()
        t2.prix = 20.0
        self.repo.list.return_value = [t1, t2]
        total, average = self.use_cases.get_total_and_average()
        self.assertEqual(total, 30.0)
        self.assertEqual(average, 15.0)

    def test_download_raises_on_parse_errors(self):
        bad_content = MagicMock()
        bad_content.text = "<html></html>"
        bad_content.url = "http://example.com/1_tome.htm"
        bad_content.name = "1_tome.htm"
        self.list_of_books_usecases.load.return_value = [bad_content]
        with self.assertRaises(ValueError):
            self.use_cases.download_list_of_books_from_url()

    def test_download_raises_if_add_many_fails(self):
        html = """<html><body>
            <table id="AutoNumber1"><tr><td><p>Mon Titre</p></td></tr></table>
            <table id="AutoNumber2">
                <tr></tr>
                <tr><td></td><td><i>Original Title</i></td></tr>
                <tr><td><p></p><p></p><p></p><p></p><p>Description du tome.</p></td></tr>
            </table>
        </body></html>"""
        content = MagicMock()
        content.text = html
        content.url = "http://example.com/1_tome.htm"
        self.list_of_books_usecases.load.return_value = [content]
        self.repo.add_many.return_value = 0  # simulate failure
        with self.assertRaises(ValueError):
            self.use_cases.download_list_of_books_from_url()


if __name__ == "__main__":
    unittest.main()
