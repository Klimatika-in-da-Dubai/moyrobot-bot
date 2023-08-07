from datetime import datetime
from sqlalchemy import ARRAY, JSON, TEXT, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("tg_user.id"))
    message_id: Mapped[int] = mapped_column(BigInteger)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    md_text: Mapped[str]
    photos: Mapped[list[str]] = mapped_column(ARRAY(TEXT))
    notify_messages_ids: Mapped[list[dict]] = mapped_column(ARRAY(JSON), default=list)
    checked: Mapped[bool] = mapped_column(default=False)
    notified: Mapped[bool] = mapped_column(default=False)
