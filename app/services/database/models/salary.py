from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class Salary(Base):
    __tablename__ = "salary"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_user.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    salary: Mapped[int]
