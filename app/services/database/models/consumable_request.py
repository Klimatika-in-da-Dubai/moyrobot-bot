from datetime import datetime
from enum import IntEnum, auto
from sqlalchemy import ARRAY, JSON, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class Consumable(IntEnum):
    SHAMPOO = auto()
    FOAM = auto()
    WAX = auto()
    COINS = auto()
    NAPKINS = auto()


class ConsumableRequest(Base):
    __tablename__ = "consumable_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    last_notify_timestamp: Mapped[datetime] = mapped_column(nullable=True)
    consumable: Mapped[Consumable] = mapped_column(Enum(Consumable))
    notify_messages_ids: Mapped[list[dict]] = mapped_column(ARRAY(JSON), default=list)
    satisfied: Mapped[bool] = mapped_column(default=False)
