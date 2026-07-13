from datetime import date

from sqlalchemy import Boolean, Date, Integer, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from persistence.sqlalchemy.entities.EntityBase import EntityBase

# attention pour terminer les relations entre entitées : from typing import List
# attention pour terminer les relations entre entitées : from typing import Optional
# attention pour terminer les relations entre entitées : from sqlalchemy import ForeignKey
# attention pour terminer les relations entre entitées : from sqlalchemy import String
# attention pour terminer les relations entre entitées : from sqlalchemy.orm import Mapped
# attention pour terminer les relations entre entitées : from sqlalchemy.orm import mapped_column
# attention pour terminer les relations entre entitées : from sqlalchemy.orm import relationship


class BookEntity(EntityBase):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(String(13))
    titre: Mapped[str] = mapped_column(Unicode(100))
    url: Mapped[str] = mapped_column(String(200))
    numero: Mapped[int] = mapped_column(Integer)
    # en attente authors: Mapped[List[Author]] = relationship( cascade="all, delete-orphan"  )

    lastParutionDate: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Unicode(1000))
    official: Mapped[bool] = mapped_column(Boolean, default=False)
    # en attente prices: list[BookPrice] = Field(default_factory=lambda: [])
    # les images etant en base 64 mais lors de leur récupération on va leur donner un non, les stocker sur un volumes dédiés et le champs images sera juste la pour avoir le nom du fichier
    image: Mapped[str] = mapped_column(Unicode(200), default="")
