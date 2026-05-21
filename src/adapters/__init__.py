from adapters.book_file_repository import BookFileRepository
from adapters.file_system import FileSystemAdapter
from adapters.html_reader import HTMLReaderAdapter
from adapters.logger import LoggerAdapter

__all__ = [
    "BookFileRepository",
    "LoggerAdapter",
    "FileSystemAdapter",
    "HTMLReaderAdapter",
]
