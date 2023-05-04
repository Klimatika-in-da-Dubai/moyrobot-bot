from aiogram.fsm.context import FSMContext

from app.services.database.models.refund import PaymentDevice, Refund
from app.services.database.models.utils import PaymentMethod


async def get_refund(state: FSMContext) -> Refund:
    data = await state.get_data()

    refund = Refund()

    columns = [
        "payment_device",
        "payment_method",
        "description",
        "statement_photo_file_id",
        "consumable_photo_file_id",
    ]

    for el in columns:
        value = data.get(el)
        if value is not None:
            refund.__setattr__(el, value)

    return refund


def get_refund_menu_text(refund: Refund) -> str:
    description = refund.description if refund.description is not None else ""

    text = "Возврат\n" f"*Причина:* {description}"
    return text


async def check_refund_report(state: FSMContext) -> bool:
    data = await state.get_data()
    not_none_colums = [
        "payment_device",
        "payment_method",
        "description",
        "statement_photo_file_id",
    ]

    refund = await get_refund(state)
    if (
        refund.payment_device == PaymentDevice.TERMINAL
        and refund.payment_method == PaymentMethod.CARD
    ):
        not_none_colums.append("money_on_card")
    else:
        not_none_colums.append("consumable_photo_file_id")
        not_none_colums.append("give_money")

    if any(data.get(el) is None for el in not_none_colums):
        return False

    return True
