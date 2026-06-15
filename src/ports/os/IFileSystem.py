from typing import Protocol


class IFileSystem(Protocol):
    """Interface for file system operations."""

    def is_file_exists(self, name: str) -> bool:
        """check if file exists

        Args:
            name (str): The name of the file to check.

        Raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        ...

    def clear(self, pattern: str) -> None:
        """Clear files matching the pattern.

        Args:
            pattern (str): The pattern to match files against.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        ...

    def list(self, pattern: str = "*.html") -> list[str]:
        """List all files matching the given pattern in the file system.

        Args:
            pattern (str): The pattern to match files against.

        Returns:
            list[str]: A list of file names matching the pattern.
        """
        ...

    def read_file(self, name: str) -> str: ...

    def write_file(self, name: str, content: str, encoding: str = "utf-8") -> None:
        """Write content to a file.

        Args:
            name (str): The name of the file to write to.
            content (str): The content to write to the file.
            encoding (str): The encoding to use when writing the file.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        ...
