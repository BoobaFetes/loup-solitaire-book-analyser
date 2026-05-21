import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import unittest
from datetime import datetime, timezone

from domain.entities.book import Book, BookPrice


class TestTomePrice(unittest.TestCase):
    def test_creation_with_required_fields(self):
        price = BookPrice(prix=12.5, source="amazon")
        self.assertEqual(price.prix, 12.5)
        self.assertEqual(price.source, "amazon")
        self.assertEqual(price.id, 0)
        self.assertIsInstance(price.date, datetime)

    def test_creation_with_all_fields(self):
        dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        price = BookPrice(id=1, prix=9.99, source="fnac", date=dt)
        self.assertEqual(price.id, 1)
        self.assertEqual(price.prix, 9.99)
        self.assertEqual(price.source, "fnac")
        self.assertEqual(price.date, dt)


class TestTome(unittest.TestCase):
    def _make_tome(self, **kwargs):
        defaults = dict(
            numero=1, titre="Titre", titre_original="Title", description="Desc"
        )
        defaults.update(kwargs)
        return Book(**defaults)

    def test_creation_sets_id_from_numero(self):
        tome = self._make_tome(numero=5)
        self.assertEqual(tome.id, 5)

    def test_creation_with_explicit_id(self):
        tome = self._make_tome(numero=5, id=99)
        self.assertEqual(tome.id, 99)

    def test_default_prices_is_empty(self):
        tome = self._make_tome()
        self.assertEqual(tome.prices, [])

    def test_date_is_set_automatically(self):
        tome = self._make_tome()
        self.assertIsInstance(tome.date, datetime)

    def test_with_prices(self):
        price = BookPrice(prix=10.0, source="amazon")
        tome = self._make_tome(prices=[price])
        self.assertEqual(len(tome.prices), 1)
        self.assertEqual(tome.prices[0].source, "amazon")

    def test_required_fields(self):
        with self.assertRaises(Exception):
            Book(numero=1)


if __name__ == "__main__":
    unittest.main()
