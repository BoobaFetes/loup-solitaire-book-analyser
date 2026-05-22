class LoggerInterface:
    def debug(self, message: str, layer: str | None = None) -> None:
        """Log a debug message.

        Args:
            message (str): The message to log.
            layer (str | None, optional): The layer from which the log is emitted. Defaults to None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def info(self, message: str, layer: str | None = None) -> None:
        """Log an info message.

        Args:
            message (str): The message to log.
            layer (str | None, optional): The layer from which the log is emitted. Defaults to None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def warning(self, message: str, layer: str | None = None) -> None:
        """Log a warning message.

        Args:
            message (str): The message to log.
            layer (str | None, optional): The layer from which the log is emitted. Defaults to None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def error(self, message: str, layer: str | None = None) -> None:
        """Log an error message.

        Args:
            message (str): The message to log.
            layer (str | None, optional): The layer from which the log is emitted. Defaults to None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def critical(self, message: str, layer: str | None = None) -> None:
        """Log a critical message.

        Args:
            message (str): The message to log.
            layer (str | None, optional): The layer from which the log is emitted. Defaults to None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError
