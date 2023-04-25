from aiogram.fsm.context import FSMContext
from app.services.database.models.promocode import WashMode
from app.utils.text import format_phone, to_correct_message


async def get_promocode_text_info(state: FSMContext) -> tuple[str, str, str]:
    phone, wash_mode, description = await get_promocode_info(state)

    phone_text = format_phone(phone) if phone is not None else ""
    wash_mode_text = str(wash_mode.value) if wash_mode is not None else ""
    description_text = description if description is not None else ""

    return (
        phone_text,
        wash_mode_text,
        description_text,
    )


async def get_promocode_text(state: FSMContext) -> str:
    phone, wash_mode, description = await get_promocode_text_info(state)

    text = (
        f"Выдать промокод\n\n"
        f"*Телефон:* {phone}\n"
        f"*Режим:* {wash_mode}\n"
        f"*Причина: * {description}\n"
    )
    return to_correct_message(text)


async def get_promocode_info(
    state: FSMContext,
) -> tuple[str | None, WashMode | None, str | None]:
    data = await state.get_data()

    phone = data.get("phone")
    wash_mode = data.get("wash_mode")
    description = data.get("description")

    if not (phone is None or isinstance(phone, str)):
        raise ValueError("Phone is not string")

    if not (wash_mode is None or isinstance(wash_mode, int)):
        raise ValueError("WashMode is not correct type")

    if not (description is None or isinstance(description, str)):
        raise ValueError("Description is not string")

    if wash_mode is not None:
        wash_mode = WashMode(wash_mode)

    return phone, wash_mode, description
