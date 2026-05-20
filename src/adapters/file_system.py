from pathlib import Path

from ports import FileSystemInterface, LoggerInterface


class FileSystemAdapter(FileSystemInterface):
    def __init__(self, logger: LoggerInterface, path: str):
        self.__logger: LoggerInterface = logger
        self.__path: Path | None = Path(path)

    def is_file_exists(self, name: str) -> bool:
        return Path(self.__path / name).exists()

    def clear(self, pattern: str):
        try:
            if pattern == "":
                raise ValueError("Pattern cannot be empty when clearing directory.")
            if self.__path.is_dir():
                for file in self.__path.glob(pattern):
                    file.unlink()
                self.__logger.info(
                    f"Cleared files matching '{pattern}' in directory: {self.__path}",
                    self.__class__.__name__,
                )
        except Exception as e:
            self.__logger.error(
                f"Error clearing directory {self.__path}: {e}", self.__class__.__name__
            )
            raise

    def list_html_files(self) -> list[str]:
        try:
            if self.__path is None:
                self.__logger.error("Path is not set for FileSystemAdapter.")
                raise ValueError("Path is not set for FileSystemAdapter.")
            return [
                str(file.name) for file in self.__path.glob("*.html") if file.is_file()
            ]
        except Exception as e:
            self.__logger.error(
                f"Error listing files in directory {self.__path}: {e}",
                self.__class__.__name__,
            )
            raise

    def read_file(self, name: str, withLog: bool = True) -> str:
        try:
            if withLog:
                self.__logger.info(
                    f"Reading file from path: {name}", self.__class__.__name__
                )

            with open(Path(self.__path / name), "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except FileNotFoundError as e:
            self.__logger.error(
                f"File not found: {Path(self.__path / name)}: {e}",
                self.__class__.__name__,
            )
            raise
        except IOError as e:
            self.__logger.error(
                f"Error reading file {Path(self.__path / name)}: {e}",
                self.__class__.__name__,
            )
            raise

    def write_file(self, name: str, content: str, withLog: bool = True):
        try:
            if withLog:
                self.__logger.info(
                    f"Writing file to path: {name}", self.__class__.__name__
                )

            current_path = Path(self.__path / name)
            # check arguments
            if current_path.suffix == "":
                self.__logger.error(
                    f"Cannot write to file path: {current_path} because it seems to be an invalid file path."
                )
                raise ValueError(f"Invalid file path: {current_path}")

            # arrange
            current_path.parent.mkdir(parents=True, exist_ok=True)
            if current_path.exists():
                current_path.unlink()

            # action
            with open(current_path, "w", encoding="utf-8") as f:
                f.write(content)
        except FileNotFoundError as e:
            self.__logger.error(
                f"File not found: {current_path}: {e}", self.__class__.__name__
            )
            raise
        except IOError as e:
            self.__logger.critical(
                f"Error reading file {current_path}: {e}", self.__class__.__name__
            )
            raise
        except Exception as e:
            self.__logger.error(
                f"Error saving file {current_path}: {e}", self.__class__.__name__
            )
            raise
