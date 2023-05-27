from datetime import datetime
from sqlalchemy import BigInteger

from sqlalchemy.orm import Mapped, mapped_column

from app.services.database.base import Base


class MoneyCollection(Base):
    __tablename__ = "money_collection"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    money_amount: Mapped[int]
    notified: Mapped[bool] = mapped_column(default=False)
