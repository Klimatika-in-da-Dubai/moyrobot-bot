from datetime import datetime
from enum import IntEnum
from sqlalchemy import BigInteger, Enum

from sqlalchemy.orm import Mapped, mapped_column

from app.services.database.base import Base


class WashMode(IntEnum):
    NONE = 0
    MODE1 = 1
    MODE2 = 2
    MODE3 = 3
    MODE4 = 4


class Promocode(Base):
    __tablename__ = "promocode"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    phone: Mapped[str]
    wash_mode: Mapped[WashMode] = mapped_column(Enum(WashMode))
    description: Mapped[str]
    sended_to_admin: Mapped[bool] = mapped_column(default=False)
