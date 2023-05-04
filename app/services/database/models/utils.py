from __future__ import annotations
from enum import IntEnum, auto


class PaymentMethod(IntEnum):
    CASH = auto()
    CARD = auto()

    @staticmethod
    def get_name(method: PaymentMethod | None) -> str:
        match method:
            case PaymentMethod.CARD:
                return "Карта"
            case PaymentMethod.CASH:
                return "Наличные"
            case None:
                return ""
