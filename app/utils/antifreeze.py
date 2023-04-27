from aiogram.fsm.context import FSMContext

from app.services.database.models.antifreeze import PaymentMethod


async def get_antifreeze_info(state: FSMContext):
    data = await state.get_data()

    payment_method = data.get("payment_method")
    payment_amount = data.get("payment_amount")

    if not (payment_method is None or isinstance(payment_method, int)):
        raise ValueError("Payment method is not correct type")

    if not (payment_amount is None or isinstance(payment_amount, int)):
        raise ValueError("Payment amount is not correct type")

    if payment_method is not None:
        payment_method = PaymentMethod(payment_method)

    return payment_method, payment_amount


async def get_antifreeze_text(state: FSMContext):
    payment_method, payment_amount = await get_antifreeze_info(state)

    payment_method_text = ""
    if payment_method == PaymentMethod.CARD:
        payment_method_text = "Карта"
    elif payment_method == PaymentMethod.CASH:
        payment_method_text = "Наличные"

    payment_amount_text = payment_amount if payment_amount is not None else ""

    text = (
        "Продажа незамерзайки\n\n"
        f"*Способ оплаты:* {payment_method_text}\n"
        f"*Сумма оплаты:* {payment_amount_text}\n"
    )

    return text
