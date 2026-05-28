from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EnvironmentInterface:
    _values: dict[str, str] = field(default_factory=dict)

    def init(self, script_root_dir: Path):
        raise NotImplementedError

    def load(self, key: str, default: str = "") -> str:
        raise NotImplementedError

    def has(self, key: str) -> bool:
        raise NotImplementedError

    def find(self, key: str, default: str = "") -> str:
        raise NotImplementedError

    def get(self, key: str) -> str:
        raise NotImplementedError

    def items(self):
        raise NotImplementedError
