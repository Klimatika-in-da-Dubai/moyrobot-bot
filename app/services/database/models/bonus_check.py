from sqlalchemy import ARRAY, JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.services.database.base import Base


class BonusCheck(Base):
    __tablename__ = "bonus_check"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    start_check: Mapped[datetime]
    end_check: Mapped[datetime]
    count_bonuses: Mapped[int]
    last_notification: Mapped[datetime] = mapped_column(default=datetime.now)
    count_notifications: Mapped[int] = mapped_column(default=0)
    checked: Mapped[bool] = mapped_column(default=False)
    alerted: Mapped[bool] = mapped_column(default=False)
    notify_messages_ids: Mapped[list[dict]] = mapped_column(ARRAY(JSON), default=list)
