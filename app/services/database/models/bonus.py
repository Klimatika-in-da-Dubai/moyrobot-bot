from datetime import datetime
from sqlalchemy import BigInteger

from sqlalchemy.orm import Mapped, mapped_column

from app.services.database.base import Base


class Bonus(Base):
    __tablename__ = "bonus"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    phone: Mapped[str]
    bonus_amount: Mapped[int]
    description: Mapped[str]
    notified: Mapped[bool] = mapped_column(default=False)
