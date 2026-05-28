import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from ports import EnvironmentInterface


@dataclass
class EnvironmentAdapter(EnvironmentInterface):
    def init(self, script_root_dir: Path):
        self.load("ENV", "dev")
        if self.get("ENV") == "dev":
            # charge les variables du fichier .env si le fichier est présent sinon récupération depuis les variable d'environnement
            load_dotenv()

        self.load("CONNECTION_STRING", "")
        self.load("LOG_FILE", "")
        self.load("LOG_LEVEL", "WARN")
        self.load(
            "FILE_SYSTEM_PATH",
            str(script_root_dir / "data")
            if self.get("ENV") != "dev"
            else str(script_root_dir.parent / "data"),
        )

    def load(self, key: str, default: str = "") -> str:
        value = os.getenv(key, default)
        self._values[key] = value
        return value

    def has(self, key: str) -> bool:
        return key in self._values

    def find(self, key: str, default: str = "") -> str:
        return self._values.get(key, default)

    def get(self, key: str) -> str:
        return self._values[key]

    def items(self):
        return self._values.items()
