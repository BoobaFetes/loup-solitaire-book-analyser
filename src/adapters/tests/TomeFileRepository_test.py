import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
from json import dumps as json_dumps
from unittest.mock import MagicMock

from adapters.tome_file_repository import TomeFileRepository
from domain import Tome


def make_tome(numero=1):
    return Tome(
        numero=numero,
        titre=f"Tome {numero}",
        titre_original=f"Title {numero}",
        description="Desc",
    )


class TestTomeFileRepository(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.fs = MagicMock()
        self.fs.is_file_exists.return_value = True
        self.fs.read_file.return_value = "{}"
        self.repo = TomeFileRepository(
            logger=self.logger, fs=self.fs, connection_string="tomes.json"
        )

    def _set_data(self, tomes: list[Tome]):
        data = {str(t.numero): t.model_dump(mode="json") for t in tomes}
        self.fs.read_file.return_value = json_dumps(data)

    def test_init_creates_file_if_not_exists(self):
        self.fs.is_file_exists.return_value = False
        TomeFileRepository(
            logger=self.logger, fs=self.fs, connection_string="tomes.json"
        )
        self.fs.write_file.assert_called_once_with("tomes.json", "{}")

    def test_list_returns_empty_when_no_data(self):
        result = self.repo.list()
        self.assertEqual(result, [])

    def test_list_returns_tomes(self):
        tome = make_tome(1)
        self._set_data([tome])
        result = self.repo.list()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].numero, 1)

    def test_add_many_returns_count(self):
        tomes = [make_tome(1), make_tome(2)]
        result = self.repo.add_many(tomes)
        self.assertEqual(result, 2)

    def test_add_returns_true(self):
        tome = make_tome(1)
        result = self.repo.add(tome)
        self.assertTrue(result)

    def test_find_returns_tome(self):
        tome = make_tome(3)
        self._set_data([tome])
        result = self.repo.find(3)
        self.assertIsNotNone(result)
        self.assertEqual(result.numero, 3)

    def test_find_returns_none_when_not_found(self):
        result = self.repo.find(999)
        self.assertIsNone(result)

    def test_get_raises_when_not_found(self):
        with self.assertRaises(ValueError):
            self.repo.get(999)

    def test_get_returns_tome(self):
        tome = make_tome(5)
        self._set_data([tome])
        result = self.repo.get(5)
        self.assertEqual(result.numero, 5)

    def test_update_returns_true_when_exists(self):
        tome = make_tome(1)
        self._set_data([tome])
        result = self.repo.update(tome)
        self.assertTrue(result)

    def test_update_returns_false_when_not_exists(self):
        tome = make_tome(999)
        result = self.repo.update(tome)
        self.assertFalse(result)

    def test_delete_returns_true_when_exists(self):
        tome = make_tome(1)
        self._set_data([tome])
        result = self.repo.delete(1)
        self.assertTrue(result)

    def test_delete_returns_false_when_not_exists(self):
        result = self.repo.delete(999)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
