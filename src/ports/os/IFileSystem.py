from pathlib import Path
from typing import Protocol


class IFileSystem(Protocol):
    """Interface for file system operations."""

    def is_dir_exists(self, path: str) -> bool:
        """check if directory exists

        Args:
            path (str): The path of the directory to check.

        Raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        ...

    def is_file_exists(self, path: str) -> bool:
        """check if file exists

        Args:
            path (str): The path of the file to check.

        Raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        ...

    def get_path(self, path: str) -> Path:
        """Get the full path of a file or directory.

        Args:
            path (str): The relative path of the file or directory.
        Raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            Path: The full path of the file or directory.
        """
        ...

    def create(self, path: str) -> None:
        """Create a directory in the file system.

        Args:
            path (str): The path of the directory to create.
        Raises:
            NotImplementedError: If the method is not implemented.
        """
        ...

    def clear(self, path: str = ".", pattern: str = "*") -> None:
        """Clear files matching the pattern.

        Args:
            path (str): The path of the directory to clear files from.
            pattern (str): The pattern to match files against.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        ...

    def list_files(self, path: str = ".", pattern: str = "*") -> list[Path]:
        """List all files matching the given pattern in the file system.

        Args:
            path (str): The path to list files from. (default: current directory or ".")
            pattern (str): The pattern to match files against.

        Returns:
            list[Path]: A list of file names matching the pattern.
        """
        ...

    def read_file(self, path: str) -> str: ...

    def read_bytes(self, path: str) -> bytes: ...

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Write content to a file.

        Args:
            path (str): The path of the file to write to.
            content (str): The content to write to the file.
            encoding (str): The encoding to use when writing the file.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        ...

    def write_bytes(self, path: str, content: bytes) -> None:
        """Write binary content to a file.

        Args:
            path (str): The path of the file to write to.
            content (bytes): The binary content to write to the file.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        ...
