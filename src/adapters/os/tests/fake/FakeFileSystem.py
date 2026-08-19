from pathlib import Path

from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeFileSystem(SpyStubFake):
    def __init__(self) -> None:
        super().__init__()
        self.files: dict[str, bytes | str] = {}

    def stub_is_dir_exists(self, returned: bool) -> None:
        self._stub("is_dir_exists", returned)

    @property
    def spy_is_dir_exists(self) -> list[SpyCall]:
        return self._spy("is_dir_exists")

    def stub_is_file_exists(self, returned: bool) -> None:
        self._stub("is_file_exists", returned)

    @property
    def spy_is_file_exists(self) -> list[SpyCall]:
        return self._spy("is_file_exists")

    def stub_get_path(self, returned: Path) -> None:
        self._stub("get_path", returned)

    @property
    def spy_get_path(self) -> list[SpyCall]:
        return self._spy("get_path")

    def stub_create(self, returned: None = None) -> None:
        self._stub("create", returned)

    @property
    def spy_create(self) -> list[SpyCall]:
        return self._spy("create")

    def stub_clear(self, returned: None = None) -> None:
        self._stub("clear", returned)

    @property
    def spy_clear(self) -> list[SpyCall]:
        return self._spy("clear")

    def stub_list(self, returned: list[str]) -> None:
        self._stub("list", returned)

    @property
    def spy_list(self) -> list[SpyCall]:
        return self._spy("list")

    def stub_list_files(self, returned: list[Path]) -> None:
        self._stub("list_files", returned)

    @property
    def spy_list_files(self) -> list[SpyCall]:
        return self._spy("list_files")

    def stub_read_file(self, returned: str) -> None:
        self._stub("read_file", returned)

    @property
    def spy_read_file(self) -> list[SpyCall]:
        return self._spy("read_file")

    def stub_read_bytes(self, returned: bytes) -> None:
        self._stub("read_bytes", returned)

    @property
    def spy_read_bytes(self) -> list[SpyCall]:
        return self._spy("read_bytes")

    def stub_write_file(self, returned: None = None) -> None:
        self._stub("write_file", returned)

    @property
    def spy_write_file(self) -> list[SpyCall]:
        return self._spy("write_file")

    def stub_write_bytes(self, returned: None = None) -> None:
        self._stub("write_bytes", returned)

    @property
    def spy_write_bytes(self) -> list[SpyCall]:
        return self._spy("write_bytes")

    def is_dir_exists(self, path: str) -> bool:
        prefix = f"{path.rstrip('/')}/"
        returned = self._returned_or_default(
            "is_dir_exists",
            any(file_path.startswith(prefix) for file_path in self.files),
        )
        return self._record_call("is_dir_exists", (path,), {}, returned)

    def is_file_exists(self, path: str) -> bool:
        returned = self._returned_or_default("is_file_exists", path in self.files)
        return self._record_call("is_file_exists", (path,), {}, returned)

    def get_path(self, path: str) -> Path:
        returned = self._returned_or_default("get_path", Path(path))
        return self._record_call("get_path", (path,), {}, returned)

    def create(self, path: str) -> None:
        returned = self._returned_or_default("create", None)
        return self._record_call("create", (path,), {}, returned)

    def clear(self, path: str = ".", pattern: str = "*") -> None:
        self.files.clear()
        returned = self._returned_or_default("clear", None)
        return self._record_call("clear", (path, pattern), {}, returned)

    def list(self, pattern: str = "*.html") -> list[str]:
        returned = self._returned_or_default("list", list(self.files))
        return self._record_call("list", (pattern,), {}, returned)

    def list_files(self, path: str = ".", pattern: str = "*") -> list[Path]:
        returned = self._returned_or_default(
            "list_files", [Path(file_path) for file_path in self.files]
        )
        return self._record_call("list_files", (path, pattern), {}, returned)

    def read_file(self, path: str) -> str:
        value = self.files[path]
        default = value if isinstance(value, str) else value.decode("utf-8")
        returned = self._returned_or_default("read_file", default)
        return self._record_call("read_file", (path,), {}, returned)

    def read_bytes(self, path: str) -> bytes:
        value = self.files[path]
        default = value if isinstance(value, bytes) else value.encode("utf-8")
        returned = self._returned_or_default("read_bytes", default)
        return self._record_call("read_bytes", (path,), {}, returned)

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> None:
        self.files[path] = content
        returned = self._returned_or_default("write_file", None)
        return self._record_call(
            "write_file", (path, content), {"encoding": encoding}, returned
        )

    def write_bytes(self, path: str, content: bytes) -> None:
        self.files[path] = content
        returned = self._returned_or_default("write_bytes", None)
        return self._record_call("write_bytes", (path, content), {}, returned)
