from enum import IntEnum, auto
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum


from app.services.database.base import Base


class MailingType(IntEnum):
    MANUAL_START_ALERT = auto()
    MANUAL_START = auto()
    SHIFT = auto()
    CLEANING = auto()
    PROMOCODE = auto()
    BONUS = auto()
    REFUND = auto()


class Mailing(Base):
    __tablename__ = "mailing"

    id: Mapped[int] = mapped_column(
        ForeignKey("tg_user.id", ondelete="CASCADE"), primary_key=True, unique=False
    )
    type: Mapped[MailingType] = mapped_column(
        Enum(MailingType), primary_key=True, unique=False
    )


class GroupMailing(Base):
    __tablename__ = "group_mailing"

    id: Mapped[int] = mapped_column(
        ForeignKey("tg_group.id", ondelete="CASCADE"), primary_key=True, unique=False
    )
    type: Mapped[MailingType] = mapped_column(
        Enum(MailingType), primary_key=True, unique=False
    )
