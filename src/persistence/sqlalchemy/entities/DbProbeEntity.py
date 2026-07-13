from datetime import datetime

from sqlalchemy import DateTime, Identity, String, func
from sqlalchemy.orm import Mapped, mapped_column

from persistence.sqlalchemy.entities.EntityBase import EntityBase


class DbProbeEntity(EntityBase):
    __tablename__ = "db_probe"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    message: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
