import enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, VARCHAR
from datetime import datetime


from app.services.database.base import Base


class ManualStartType(enum.Enum):
    TEST = "test"
    REWASH = "rewash"
    PAID = "paid"


class ManualStart(Base):
    __tablename__ = "manual_start"

    id: Mapped[str] = mapped_column(
        VARCHAR(10), primary_key=True, unique=True, nullable=False
    )
    date: Mapped[datetime] = mapped_column()
    mode: Mapped[int] = mapped_column(nullable=True)
    reported: Mapped[bool] = mapped_column(default=False)
    sended_to_admin: Mapped[bool] = mapped_column(default=False)
    type: Mapped[ManualStartType] = mapped_column(
        Enum(ManualStartType), nullable=True, default=None
    )


class TestManualStart(ManualStart):
    __tablename__ = "test_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    description: Mapped[str]


class RewashManualStart(ManualStart):
    __tablename__ = "rewash_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    photo_file_id: Mapped[str]
    description: Mapped[str]


class PaidManualStart(ManualStart):
    __tablename__ = "paid_manual_start"

    id: Mapped[str] = mapped_column(
        ForeignKey("manual_start.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    payment_method: Mapped[str]
    payment_amount: Mapped[int]