import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
from unittest.mock import MagicMock, patch

import httpx

from adapters.html_reader import HTMLReaderAdapter
from domain import URLContent


class TestHTMLReaderAdapter(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        with patch("logging.getLogger"):
            self.adapter = HTMLReaderAdapter(logger=self.logger)

    def test_load_returns_url_content(self):
        mock_response = MagicMock()
        mock_response.content = "<html>test</html>".encode("latin-1")
        mock_response.raise_for_status = MagicMock()
        with patch("httpx.get", return_value=mock_response):
            result = self.adapter.load("http://example.com")
            self.assertIsInstance(result, URLContent)
            self.assertEqual(result.url, "http://example.com")

    def test_load_raises_on_http_error(self):
        with patch("httpx.get", side_effect=httpx.HTTPError("error")):
            with self.assertRaises(httpx.HTTPError):
                self.adapter.load("http://example.com")

    def test_load_raises_on_request_error(self):
        with patch("httpx.get", side_effect=httpx.RequestError("error")):
            with self.assertRaises(httpx.RequestError):
                self.adapter.load("http://example.com")

    def test_prettify_html_returns_string(self):
        result = self.adapter.prettify_html("<html><body></body></html>")
        self.assertIsInstance(result, str)
        self.assertIn("<html>", result)

    def test_select_by_selector_returns_elements(self):
        content = URLContent(
            url="http://x.com", text="<html><body><p class='t'>Hello</p></body></html>"
        )
        result = self.adapter.select_by_selector(content, "p.t")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get_text(), "Hello")

    def test_select_by_selector_empty_result(self):
        content = URLContent(url="http://x.com", text="<html><body></body></html>")
        result = self.adapter.select_by_selector(content, "p.nonexistent")
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
