from enum import IntEnum, auto
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, VARCHAR
from datetime import datetime


from app.services.database.base import Base
from app.services.database.models.corporation import Corporation
from app.services.database.models.utils import PaymentMethod


class ManualStartType(IntEnum):
    TEST = auto()
    REWASH = auto()
    PAID = auto()
    SERVICE = auto()
    CORPORATE = auto()


class ManualStart(Base):
    __tablename__ = "manual_start"

    id: Mapped[str] = mapped_column(
        VARCHAR(10), primary_key=True, unique=True, nullable=False
    )
    terminal_id: Mapped[int]
    date: Mapped[datetime]
    mode: Mapped[int] = mapped_column(nullable=True)
    type: Mapped[ManualStartType] = mapped_column(
        Enum(ManualStartType), nullable=True, default=None
    )
    reported: Mapped[bool] = mapped_column(default=False)
    report_reminded: Mapped[bool] = mapped_column(default=False)
    report_alerted: Mapped[bool] = mapped_column(default=False)
    notified: Mapped[bool] = mapped_column(default=False)


class TestManualStart(Base):
    __tablename__ = "test_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    photo_file_id: Mapped[str]
    description: Mapped[str]


class ServiceManualStart(Base):
    __tablename__ = "service_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    photo_file_id: Mapped[str]
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
    photo_file_id: Mapped[str]


class CorporateManualStart(Base):
    __tablename__ = "corporate_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    corporation_id: Mapped[int] = mapped_column(ForeignKey("corporation.id"))
    description: Mapped[str]
    photo_file_id: Mapped[str]
