import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest

from ports.book_repository import BookRepositoryInterface


class TestTomeRepositoryInterface(unittest.TestCase):
    def setUp(self):
        self.repo = BookRepositoryInterface()

    def test_list_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repo.list()

    def test_add_many_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repo.add_many([])

    def test_add_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repo.add(MagicMock())

    def test_get_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repo.get(1)

    def test_find_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repo.find(1)

    def test_update_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repo.update(MagicMock())

    def test_delete_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.repo.delete(1)


from unittest.mock import MagicMock

if __name__ == "__main__":
    unittest.main()
