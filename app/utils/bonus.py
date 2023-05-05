from aiogram.fsm.context import FSMContext

from app.utils.text import escape_chars, format_phone


async def get_bonus_info(
    state: FSMContext,
) -> tuple[str | None, int | None, str | None]:
    data = await state.get_data()

    phone = data.get("phone")
    bonus_amount = data.get("bonus_amount")
    description = data.get("description")

    if not (phone is None or isinstance(phone, str)):
        raise ValueError("phone is not correct type")

    if not (bonus_amount is None or isinstance(bonus_amount, int)):
        raise ValueError("phone is not correct type")

    if not (description is None or isinstance(description, str)):
        raise ValueError("phone is not correct type")

    return phone, bonus_amount, description


async def get_bonus_text(state: FSMContext):
    phone, bonus, description = await get_bonus_info(state)

    phone_text = escape_chars(format_phone(phone)) if phone is not None else ""
    bonus_text = escape_chars(str(bonus)) if bonus is not None else ""
    description_text = escape_chars(description) if description is not None else ""

    text = (
        "Начислить бонусы\n\n"
        f"*Телефон:* {phone_text}\n"
        f"*Количество бонусов:* {bonus_text}\n"
        f"*Причина:* {description_text}\n"
    )

    return text
