from datetime import datetime
from sqlalchemy import ARRAY, TEXT, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("tg_user.id"))
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    text: Mapped[str]
    photos: Mapped[list[str]] = mapped_column(ARRAY(TEXT))
    checked: Mapped[bool] = mapped_column(default=False)
    notified: Mapped[bool] = mapped_column(default=False)
