from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class Corporation(Base):
    __tablename__ = "corporation"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str]
