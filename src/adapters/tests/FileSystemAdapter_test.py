import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from adapters.file_system import FileSystemAdapter


class TestFileSystemAdapter(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.tmp_path = "/tmp/test_fs"
        self.adapter = FileSystemAdapter(logger=self.logger, path=self.tmp_path)

    def test_is_file_exists_true(self):
        with patch.object(Path, "exists", return_value=True):
            self.assertTrue(self.adapter.is_file_exists("file.json"))

    def test_is_file_exists_false(self):
        with patch.object(Path, "exists", return_value=False):
            self.assertFalse(self.adapter.is_file_exists("file.json"))

    def test_clear_raises_on_empty_pattern(self):
        with self.assertRaises(ValueError):
            self.adapter.clear("")

    def test_clear_deletes_matching_files(self):
        mock_file = MagicMock()
        with (
            patch.object(Path, "is_dir", return_value=True),
            patch.object(Path, "glob", return_value=[mock_file]),
        ):
            self.adapter.clear("*.html")
            mock_file.unlink.assert_called_once()

    def test_list_html_files_returns_names(self):
        mock_file = MagicMock()
        mock_file.name = "test.html"
        mock_file.is_file.return_value = True
        with patch.object(Path, "glob", return_value=[mock_file]):
            result = self.adapter.list_html_files()
            self.assertIn("test.html", result)

    def test_read_file_returns_content(self):
        with patch("builtins.open", mock_open(read_data="content")):
            result = self.adapter.read_file("file.json", withLog=False)
            self.assertEqual(result, "content")

    def test_read_file_raises_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                self.adapter.read_file("missing.json")

    def test_write_file_raises_on_no_extension(self):
        with self.assertRaises(ValueError):
            self.adapter.write_file("noextension", "content")

    def test_write_file_writes_content(self):
        m = mock_open()
        with (
            patch("builtins.open", m),
            patch.object(
                Path, "parent", new_callable=lambda: property(lambda self: MagicMock())
            ),
            patch.object(Path, "exists", return_value=False),
        ):
            self.adapter.write_file("file.json", "{}", withLog=False)
            m().write.assert_called_once_with("{}")


if __name__ == "__main__":
    unittest.main()
