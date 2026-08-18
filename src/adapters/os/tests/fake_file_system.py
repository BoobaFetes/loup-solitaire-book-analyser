class FakeFileSystem:
    def __init__(self) -> None:
        self.files: dict[str, bytes | str] = {}

    def is_file_exists(self, name: str) -> bool:
        return name in self.files

    def clear(self, pattern: str) -> None:
        self.files.clear()

    def list(self, pattern: str = "*.html") -> list[str]:
        return list(self.files)

    def read_file(self, name: str) -> str:
        value = self.files[name]
        return value if isinstance(value, str) else value.decode("utf-8")

    def read_bytes(self, name: str) -> bytes:
        value = self.files[name]
        return value if isinstance(value, bytes) else value.encode("utf-8")

    def write_file(self, name: str, content: str, encoding: str = "utf-8") -> None:
        self.files[name] = content

    def write_bytes(self, name: str, content: bytes) -> None:
        self.files[name] = content
