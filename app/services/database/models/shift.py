from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column

from app.services.database.base import Base


class Shift(Base):
    __tablename__ = "shift"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    open_date: Mapped[datetime] = mapped_column(nullable=True)
    opened_by_id: Mapped[int] = mapped_column(ForeignKey("tg_user.id"))
    close_date: Mapped[datetime] = mapped_column(nullable=True)
    closed_by_id: Mapped[int] = mapped_column(ForeignKey("tg_user.id"), nullable=True)


class OpenShift(Base):
    __tablename__ = "open_shift"

    id: Mapped[int] = mapped_column(
        ForeignKey("shift.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    money_amount: Mapped[int] = mapped_column(default=0)
    antifreeze_count: Mapped[int] = mapped_column(default=0)
    chemistry_count: Mapped[int] = mapped_column(default=0)
    chemistry_check: Mapped[bool] = mapped_column(default=False)
    equipment_check: Mapped[bool] = mapped_column(default=False)
    robot_movement_check: Mapped[bool] = mapped_column(default=False)
    robot_leak_check: Mapped[bool] = mapped_column(default=False)
    gates_check: Mapped[bool] = mapped_column(default=False)
    cleaning_check: Mapped[bool] = mapped_column(default=True)


class CloseShift(Base):
    __tablename__ = "close_shift"

    id: Mapped[int] = mapped_column(
        ForeignKey("shift.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    money_amount: Mapped[int] = mapped_column(default=0, nullable=False)
    antifreeze_count: Mapped[int] = mapped_column(default=0)
    chemistry_count: Mapped[int] = mapped_column(default=0)
    chemistry_check: Mapped[bool] = mapped_column(default=False)
    equipment_check: Mapped[bool] = mapped_column(default=False)
    robot_leak_check: Mapped[bool] = mapped_column(default=False)
    gates_check: Mapped[bool] = mapped_column(default=False)
