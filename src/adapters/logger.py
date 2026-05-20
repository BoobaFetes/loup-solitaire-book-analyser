import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from ports import LoggerInterface


class LoggerAdapter(LoggerInterface):
    def __init__(self, log_file: str = "logs/app.log", log_level: str = "INFO"):
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                # permet de faire une rotation des logs tous les jours à minuit et conservation des 31 derniers jours de log
                TimedRotatingFileHandler(
                    filename=log_file,
                    when="midnight",  # Rotate at midnight
                    interval=1,  # Rotate daily
                    backupCount=31,  # Keep 31 days of logs
                ),
                # garde aussi les logs console pour faciliter le développement et le debug ou voir directement dans k8s
                logging.StreamHandler(),
            ],
        )
        self.__logger = logging.getLogger(__name__)

    def debug(self, message: str, layer: str = None):
        self.__log_with_level("DEBUG", message, layer)

    def info(self, message: str, layer: str = None):
        self.__log_with_level("INFO", message, layer)

    def warning(self, message: str, layer: str = None):
        self.__log_with_level("WARNING", message, layer)

    def error(self, message: str, layer: str = None):
        self.__log_with_level("ERROR", message, layer)

    def critical(self, message: str, layer: str = None):
        self.__log_with_level("CRITICAL", message, layer)

    def __log_with_level(self, level: str, message: str, layer: str = None):
        msg = f"[{layer}] {message}" if layer else message
        self.__logger.log(getattr(logging, level), msg)
