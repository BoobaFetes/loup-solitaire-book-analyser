import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestLoggerAdapter(unittest.TestCase):
    def _make_logger(self, log_level="DEBUG"):
        with (
            patch.object(Path, "mkdir"),
            patch("logging.basicConfig"),
            patch(
                "adapters.logger.TimedRotatingFileHandler"
            ),  # évite l'ouverture du fichier
            patch("logging.getLogger", return_value=MagicMock()),
        ):
            from adapters.logger import LoggerAdapter

            return LoggerAdapter(log_file="/tmp/test.log", log_level=log_level)

    def test_debug_calls_log(self):
        logger = self._make_logger()
        logger._LoggerAdapter__logger = MagicMock()
        logger.debug("test message")
        logger._LoggerAdapter__logger.log.assert_called_once()

    def test_info_calls_log(self):
        logger = self._make_logger()
        logger._LoggerAdapter__logger = MagicMock()
        logger.info("info message")
        logger._LoggerAdapter__logger.log.assert_called_once()

    def test_warning_calls_log(self):
        logger = self._make_logger()
        logger._LoggerAdapter__logger = MagicMock()
        logger.warning("warn message")
        logger._LoggerAdapter__logger.log.assert_called_once()

    def test_error_calls_log(self):
        logger = self._make_logger()
        logger._LoggerAdapter__logger = MagicMock()
        logger.error("error message")
        logger._LoggerAdapter__logger.log.assert_called_once()

    def test_critical_calls_log(self):
        logger = self._make_logger()
        logger._LoggerAdapter__logger = MagicMock()
        logger.critical("critical message")
        logger._LoggerAdapter__logger.log.assert_called_once()

    def test_log_with_layer_formats_message(self):
        logger = self._make_logger()
        logger._LoggerAdapter__logger = MagicMock()
        logger.info("msg", "LAYER")
        call_args = logger._LoggerAdapter__logger.log.call_args[0]
        self.assertIn("[LAYER]", call_args[1])
        self.assertIn("msg", call_args[1])

    def test_log_without_layer(self):
        logger = self._make_logger()
        logger._LoggerAdapter__logger = MagicMock()
        logger.info("msg")
        call_args = logger._LoggerAdapter__logger.log.call_args[0]
        self.assertEqual(call_args[1], "msg")


if __name__ == "__main__":
    unittest.main()
