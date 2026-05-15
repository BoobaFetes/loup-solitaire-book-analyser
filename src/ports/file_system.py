class FileSystemInterface:
    def is_file_exists(self, name: str) -> bool:
        raise NotImplementedError

    def clear(self, pattern: str):
        raise NotImplementedError

    def list_html_files(self) -> list[str]:
        raise NotImplementedError

    def read_file(self, name: str, withLog: bool = True) -> str:
        raise NotImplementedError

    def write_file(self, name: str, content: str, withLog: bool = True):
        raise NotImplementedError
