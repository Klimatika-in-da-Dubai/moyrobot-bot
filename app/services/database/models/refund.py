from __future__ import annotations
from datetime import datetime
from enum import IntEnum, auto
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database.base import Base
from app.services.database.models.utils import PaymentMethod


class PaymentDevice(IntEnum):
    CASHBOX = auto()
    TERMINAL = auto()

    @staticmethod
    def get_name(device: PaymentDevice | None) -> str:
        match device:
            case PaymentDevice.CASHBOX:
                return "Касса"
            case PaymentDevice.TERMINAL:
                return "Терминал"
            case None:
                return ""


class Refund(Base):
    __tablename__ = "refund"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    payment_device: Mapped[PaymentDevice]
    payment_method: Mapped[PaymentMethod]
    description: Mapped[str]
    statement_photo_file_id: Mapped[str]
    consumable_photo_file_id: Mapped[str] = mapped_column(nullable=True)
