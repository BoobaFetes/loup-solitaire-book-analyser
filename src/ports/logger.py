class LoggerInterface:
    def debug(self, message: str, layer: str = None):
        raise NotImplementedError

    def info(self, message: str, layer: str = None):
        raise NotImplementedError

    def warning(self, message: str, layer: str = None):
        raise NotImplementedError

    def error(self, message: str, layer: str = None):
        raise NotImplementedError

    def critical(self, message: str, layer: str = None):
        raise NotImplementedError
