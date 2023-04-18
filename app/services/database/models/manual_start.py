from enum import IntEnum, auto
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, VARCHAR
from datetime import datetime


from app.services.database.base import Base


class ManualStartType(IntEnum):
    TEST = auto()
    REWASH = auto()
    PAID = auto()
    SERVICE = auto()


class PaymentMethod(IntEnum):
    CASH = auto()
    CARD = auto()


class ManualStart(Base):
    __tablename__ = "manual_start"

    id: Mapped[str] = mapped_column(
        VARCHAR(10), primary_key=True, unique=True, nullable=False
    )
    terminal_id: Mapped[int]
    date: Mapped[datetime]
    mode: Mapped[int] = mapped_column(nullable=True)
    reported: Mapped[bool] = mapped_column(default=False)
    sended_to_chat: Mapped[bool] = mapped_column(default=False)
    sended_to_admin: Mapped[bool] = mapped_column(default=False)
    type: Mapped[ManualStartType] = mapped_column(
        Enum(ManualStartType), nullable=True, default=None
    )


class TestManualStart(Base):
    __tablename__ = "test_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    description: Mapped[str]


class ServiceManualStart(Base):
    __tablename__ = "service_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    description: Mapped[str]


class RewashManualStart(Base):
    __tablename__ = "rewash_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    photo_file_id: Mapped[str]
    description: Mapped[str]


class PaidManualStart(Base):
    __tablename__ = "paid_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    payment_method: Mapped[PaymentMethod]
    payment_amount: Mapped[int]
