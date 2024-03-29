from datetime import datetime
from sqlalchemy import ARRAY, JSON, TEXT, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class OperatorRequest(Base):
    __tablename__ = "operator_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("tg_user.id"))
    message_id: Mapped[int] = mapped_column(BigInteger)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    last_notify_timestamp: Mapped[datetime] = mapped_column(nullable=True)
    md_text: Mapped[str]
    photos: Mapped[list[str]] = mapped_column(ARRAY(TEXT), default=list)
    notify_messages_ids: Mapped[list[dict]] = mapped_column(ARRAY(JSON), default=list)
    satisfied: Mapped[bool] = mapped_column(default=False)
