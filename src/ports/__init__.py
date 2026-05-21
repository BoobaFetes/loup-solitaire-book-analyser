from ports.book_repository import BookRepositoryInterface
from ports.file_system import FileSystemInterface
from ports.html_reader import HTMLReaderInterface
from ports.logger import LoggerInterface

__all__ = [
    "BookRepositoryInterface",
    "LoggerInterface",
    "FileSystemInterface",
    "HTMLReaderInterface",
]
