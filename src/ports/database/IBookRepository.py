from typing import Literal, Protocol, TypeVar

from domain import Book
from ports.database.IRepository import IRepository

TId = TypeVar("TId", bound=int, contravariant=True)
TBookListField = Literal["id", "isbn", "titre", "numero"]


class IBookRepository(IRepository[Book, TId, TBookListField], Protocol):
    pass
