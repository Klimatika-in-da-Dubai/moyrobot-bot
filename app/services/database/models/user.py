import enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum


from app.services.database.base import Base


class Role(enum.Enum):
    OPERATOR = "operator"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "tg_user"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str]


class UserRole(Base):
    __tablename__ = "tg_user_role"

    id: Mapped[int] = mapped_column(
        ForeignKey("tg_user.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[Role] = mapped_column(Enum(Role), primary_key=True)
