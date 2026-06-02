class FileSystemInterface:
    """ """

    def is_file_exists(self, name: str) -> bool:
        """check if file exists

        Args:
            name (str): The name of the file to check.

        Raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        raise NotImplementedError

    def clear(self, pattern: str) -> None:
        """Clear files matching the pattern.

        Args:
            pattern (str): The pattern to match files against.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def list_html_files(self) -> list[str]:
        """List all HTML files in the file system.

        Returns:
            list[str]: A list of HTML file names.
        """
        raise NotImplementedError

    def read_file(self, name: str) -> str:
        raise NotImplementedError

    def write_file(self, name: str, content: str) -> None:
        """Write content to a file.

        Args:
            name (str): The name of the file to write to.
            content (str): The content to write to the file.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError
