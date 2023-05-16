from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class ShiftsDifference(Base):
    __tablename__ = "shifts_difference"

    closed_shift_id: Mapped[int] = mapped_column(
        ForeignKey("shift.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    opened_shift_id: Mapped[int] = mapped_column(
        ForeignKey("shift.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    money_difference: Mapped[int]
    notified: Mapped[bool] = mapped_column(default=False)
