from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class ShiftCheck(Base):
    __tablename__ = "shift_check"

    id: Mapped[int] = mapped_column(
        ForeignKey("shift.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    money_expected: Mapped[int]
    money_actual: Mapped[int]
    money_difference: Mapped[int]
    notified: Mapped[bool] = mapped_column(default=False)
