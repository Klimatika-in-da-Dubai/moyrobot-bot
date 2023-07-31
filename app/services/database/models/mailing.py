from enum import IntEnum, auto
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, BigInteger


from app.services.database.base import Base


class MailingType(IntEnum):
    MONTHLY_REPORT = auto()
    MANUAL_START_REPORT_ALERT = auto()
    MANUAL_START_REPORT_REMIND = auto()
    MANUAL_START = auto()
    SHIFT = auto()
    SHIFT_CHECK = auto()
    SHIFTS_DIFFERENCE = auto()
    ANTIFREEZE = auto()
    CLEANING = auto()
    PROMOCODE = auto()
    PROMOCODE_CHECK = auto()
    BONUS = auto()
    BONUS_CHECK = auto()
    REFUND = auto()
    PAYMENT_CHECK = auto()
    PAYMENT_CHECK_ALERT = auto()
    MONEY_COLLECTION = auto()
    CORPORATE_REPORT = auto()


class Mailing(Base):
    __tablename__ = "mailing"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_user.id", ondelete="CASCADE"),
        primary_key=True,
        unique=False,
    )
    type: Mapped[MailingType] = mapped_column(
        Enum(MailingType), primary_key=True, unique=False
    )


class GroupMailing(Base):
    __tablename__ = "group_mailing"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_group.id", ondelete="CASCADE"),
        primary_key=True,
        unique=False,
    )
    type: Mapped[MailingType] = mapped_column(
        Enum(MailingType), primary_key=True, unique=False
    )
