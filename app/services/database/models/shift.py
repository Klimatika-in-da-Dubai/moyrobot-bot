from datetime import datetime, time, timedelta
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
    closed_automaticaly: Mapped[bool] = mapped_column(default=False)
    notified: Mapped[bool] = mapped_column(default=False)
    monthly_reported: Mapped[bool] = mapped_column(default=False)

    def is_daily_shift(self) -> bool:
        return (
            time.fromisoformat("06:00")
            <= self.open_date.time()
            < time.fromisoformat("18:00")
        )

    def is_nightly_shift(self) -> bool:
        return time.fromisoformat(
            "18:00"
        ) <= self.open_date.time() or self.open_date.time() < time.fromisoformat(
            "06:00"
        )

    def is_should_be_closed(self) -> bool:
        if self.close_date is not None:
            return False

        if self.is_daily_shift() and (
            datetime.now().time() > time.fromisoformat("21:30")
        ):
            return True

        if self.is_nightly_shift() and (
            time.fromisoformat("09:30")
            < datetime.now().time()
            < time.fromisoformat("18:00")
        ):
            return True

        if datetime.now() - self.open_date > timedelta(seconds=15 * 60 * 60):
            return True

        return False


class OpenShift(Base):
    __tablename__ = "open_shift"

    id: Mapped[int] = mapped_column(
        ForeignKey("shift.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    money_amount: Mapped[int] = mapped_column(default=0)
    antifreeze_count: Mapped[int] = mapped_column(default=0)
    chemistry_count: Mapped[int] = mapped_column(default=0)
    chemistry_check: Mapped[bool] = mapped_column(default=False)
    equipment_check: Mapped[bool] = mapped_column(default=False)
    robot_movement_check: Mapped[bool] = mapped_column(default=False)
    robot_leak_check: Mapped[bool] = mapped_column(default=False)
    gates_check: Mapped[bool] = mapped_column(default=False)
    cleaning_check: Mapped[bool] = mapped_column(default=True)
    notified: Mapped[bool] = mapped_column(default=False)


class CloseShift(Base):
    __tablename__ = "close_shift"

    id: Mapped[int] = mapped_column(
        ForeignKey("shift.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    money_amount: Mapped[int] = mapped_column(default=0, nullable=False)
    antifreeze_count: Mapped[int] = mapped_column(default=0)
    chemistry_count: Mapped[int] = mapped_column(default=0)
    chemistry_check: Mapped[bool] = mapped_column(default=False)
    equipment_check: Mapped[bool] = mapped_column(default=False)
    robot_movement_check: Mapped[bool] = mapped_column(default=False)
    robot_leak_check: Mapped[bool] = mapped_column(default=False)
    gates_check: Mapped[bool] = mapped_column(default=False)
    notified: Mapped[bool] = mapped_column(default=False)
