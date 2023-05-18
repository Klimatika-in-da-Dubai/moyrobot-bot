from datetime import datetime
from sqlalchemy import BigInteger

from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base
from app.services.database.models.utils import PaymentMethod


class Antifreeze(Base):
    __tablename__ = "antifreeze"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    payment_method: Mapped[PaymentMethod]
    payment_amount: Mapped[int]
    notified: Mapped[bool] = mapped_column(default=False)
