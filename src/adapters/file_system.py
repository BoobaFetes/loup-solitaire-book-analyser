from pathlib import Path

from ports import FileSystemInterface, LoggerInterface


class FileSystemAdapter(FileSystemInterface):
    """Adaptateur pour l'interface du système de fichiers.

    Args:
        FileSystemInterface: L'interface du système de fichiers.
    """

    def __init__(self, logger: LoggerInterface, path: str):
        self.__logger: LoggerInterface = logger
        self.__path: Path = Path(path)

    def is_file_exists(self, name: str) -> bool:
        """Check if a file exists in the file system.

        Args:
            name (str): The name of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return Path(self.__path / name).exists()

    def clear(self, pattern: str):
        """Clear files matching the given pattern in the file system.

        Args:
            pattern (str): The glob pattern to match files for deletion.

        Raises:
            ValueError: If the pattern is empty.
        """
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
            self.__logger.critical(
                f"Error clearing directory {self.__path}: {e}", self.__class__.__name__
            )
            raise

    def list_html_files(self) -> list[str]:
        """List all HTML files in the directory.

        Returns:
            list[str]: A list of HTML file names.
        """
        return [str(file.name) for file in self.__path.glob("*.html") if file.is_file()]

    def read_file(self, name: str, withLog: bool = True) -> str:
        """Read the contents of a file.

        Args:
            name (str): The name of the file to read.
            withLog (bool, optional): Whether to log the read operation. Defaults to True.


        Raises:
            FileNotFoundError: If the file is not found.
            IOError: If there is an error reading the file.

        Returns:
            str: The contents of the file.
        """
        try:
            if withLog:
                self.__logger.info(
                    f"Reading file from path: {name}", self.__class__.__name__
                )

            with open(Path(self.__path / name), "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except FileNotFoundError as e:
            self.__logger.critical(
                f"File not found: {Path(self.__path / name)}: {e}",
                self.__class__.__name__,
            )
            raise
        except IOError as e:
            self.__logger.critical(
                f"Error reading file {Path(self.__path / name)}: {e}",
                self.__class__.__name__,
            )
            raise

    def write_file(self, name: str, content: str, withLog: bool = True) -> None:
        """Write the contents to a file.

        Args:
            name (str): The name of the file to write.
            content (str): The contents to write to the file.
            withLog (bool, optional): Whether to log the write operation. Defaults to True.

        Raises:
            ValueError: If the file path is invalid.
            FileNotFoundError: If the file is not found.
            IOError: If there is an error writing to the file.
            Exception: If there is any other error during the file writing process.
        """
        current_path: Path = Path(self.__path / name)
        try:
            if withLog:
                self.__logger.info(
                    f"Writing file to path: {name}", self.__class__.__name__
                )

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
            self.__logger.critical(
                f"File not found: {current_path}: {e}", self.__class__.__name__
            )
            raise
        except IOError as e:
            self.__logger.critical(
                f"Error reading file {current_path}: {e}", self.__class__.__name__
            )
            raise
        except Exception as e:
            self.__logger.critical(
                f"Error saving file {current_path}: {e}", self.__class__.__name__
            )
            raise
