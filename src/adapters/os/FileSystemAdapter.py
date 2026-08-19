import logging
from pathlib import Path

from ports.os import IFileSystem


class FileSystemAdapter(IFileSystem):
    """Adaptateur pour l'interface du système de fichiers.

    Args:
        IFileSystem: L'interface du système de fichiers.
    """

    def __init__(self, path: str):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._path: Path = Path(path)

    def is_dir_exists(self, path: str) -> bool:
        """check if directory exists

        Args:
            path (str): The path of the directory to check.

        Raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        return Path(self._path / path).is_dir()

    def is_file_exists(self, path: str) -> bool:
        """Check if a file exists in the file system.

        Args:
            path (str): The path of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return Path(self._path / path).is_file()

    def get_path(self, path: str) -> Path:
        """Get the full path of a file or directory.

        Args:
            path (str): The relative path of the file or directory.
        Returns:
            Path: The full path of the file or directory.
        """
        return Path(self._path / path).resolve()

    def create(self, path: str) -> None:
        """Create a directory in the file system.

        Args:
            path (str): The path of the directory to create.
        """
        Path(self._path / path).mkdir(parents=True, exist_ok=True)

    def clear(self, path: str = ".", pattern: str = "*"):
        """Clear files matching the given pattern in the file system.

        Args:
            path (str): The path of the directory to clear files from.
            pattern (str): The glob pattern to match files for deletion.

        Raises:
            ValueError: If the pattern is empty.
        """
        try:
            if pattern == "":
                raise ValueError("Pattern cannot be empty when clearing directory.")
            target_dir = self._path / path
            if target_dir.is_dir():
                for file in target_dir.glob(pattern):
                    file.unlink()
                self._logger.info(
                    f"Cleared files matching '{pattern}' in directory: {target_dir}",
                )
        except Exception as e:
            self._logger.critical(
                f"Error clearing directory {self._path}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise

    def list_files(self, path: str = ".", pattern: str = "*") -> list[Path]:
        """List all files matching the given pattern in the file system.

        Args:
            path (str): The path of the directory to list files from.
            pattern (str): The pattern to match files against.

        Returns:
            list[Path]: A list of file names matching the pattern.
        """
        return [
            file for file in Path(self._path / path).glob(pattern) if file.is_file()
        ]

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """Read the contents of a file.

        Args:
            path (str): The path of the file to read.


        Raises:
            FileNotFoundError: If the file is not found.
            IOError: If there is an error reading the file.

        Returns:
            str: The contents of the file.
        """
        try:
            with open(Path(self._path / path), "r", encoding=encoding) as f:
                content = f.read()
            return content
        except FileNotFoundError as e:
            self._logger.critical(
                f"File not found: {Path(self._path / path)}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except IOError as e:
            self._logger.critical(
                f"Error reading file {Path(self._path / path)}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise

    def read_bytes(self, path: str) -> bytes:
        """Read the binary contents of a file.

        Args:
            path (str): The path of the file to read.

        Raises:
            FileNotFoundError: If the file is not found.
            IOError: If there is an error reading the file.

        Returns:
            bytes: The binary contents of the file.
        """
        current_path: Path = Path(self._path / path)
        try:
            with open(current_path, "rb") as f:
                return f.read()
        except FileNotFoundError as e:
            self._logger.critical(
                f"File not found: {current_path}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except IOError as e:
            self._logger.critical(
                f"Error reading file {current_path}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Write the contents to a file.

        Args:
            path (str): The path of the file to write.
            content (str): The contents to write to the file.
            encoding (str): The encoding to use when writing the file.

        Raises:
            ValueError: If the file path is invalid.
            FileNotFoundError: If the file is not found.
            IOError: If there is an error writing to the file.
            Exception: If there is any other error during the file writing process.
        """
        current_path: Path = Path(self._path / path)
        try:
            # check arguments
            if current_path.suffix == "":
                self._logger.error(
                    f"Cannot write to file path: {current_path} because it seems to be an invalid file path."
                )
                raise ValueError(f"Invalid file path: {current_path}")

            # arrange
            current_path.parent.mkdir(parents=True, exist_ok=True)
            if current_path.exists():
                current_path.unlink()

            # action
            with open(current_path, "w", encoding=encoding) as f:
                f.write(content)
        except FileNotFoundError as e:
            self._logger.critical(
                f"File not found: {current_path}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise

    def write_bytes(self, path: str, content: bytes) -> None:
        """Write binary contents to a file.

        Args:
            path (str): The path of the file to write.
            content (bytes): The binary contents to write.

        Raises:
            ValueError: If the file path is invalid.
            FileNotFoundError: If the file is not found.
            IOError: If there is an error writing to the file.
            Exception: If there is any other error during the file writing process.
        """
        current_path: Path = Path(self._path / path)
        try:
            if current_path.suffix == "":
                self._logger.error(
                    f"Cannot write to file path: {current_path} because it seems to be an invalid file path."
                )
                raise ValueError(f"Invalid file path: {current_path}")

            current_path.parent.mkdir(parents=True, exist_ok=True)
            if current_path.exists():
                current_path.unlink()

            with open(current_path, "wb") as f:
                f.write(content)
        except FileNotFoundError as e:
            self._logger.critical(
                f"File not found: {current_path}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except IOError as e:
            self._logger.critical(
                f"Error writing file {current_path}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
        except Exception as e:
            self._logger.critical(
                f"Error saving file {current_path}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
