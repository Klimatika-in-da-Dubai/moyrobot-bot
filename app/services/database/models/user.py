from enum import IntEnum, auto
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, BigInteger


from app.services.database.base import Base


class Role(IntEnum):
    OPERATOR = auto()
    MODERATOR = auto()
    ADMIN = auto()


class User(Base):
    __tablename__ = "tg_user"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, autoincrement=False
    )
    name: Mapped[str]


class UserRole(Base):
    __tablename__ = "tg_user_role"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_user.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    role: Mapped[Role] = mapped_column(Enum(Role), primary_key=True)
