from aiogram.fsm.context import FSMContext

from app.services.database.models.shift import CloseShift, OpenShift


shift_info_columns = [
    "money_amount",
    "antifreeze_count",
    "shampoo_count",
    "foam_count",
    "wax_count",
    "shampoo_check",
    "foam_check",
    "wax_check",
    "equipment_check",
    "robot_movement_check",
    "robot_leak_check",
    "gates_check",
]


async def get_open_shift(state: FSMContext) -> OpenShift:
    data = await state.get_data()

    shift = OpenShift()

    columns = shift_info_columns + ["cleaning_check"]

    for el in columns:
        value = data.get(el)
        if value is not None:
            shift.__setattr__(el, value)

    return shift


async def get_close_shift(state: FSMContext) -> CloseShift:
    data = await state.get_data()

    shift = CloseShift()

    columns = shift_info_columns

    for el in columns:
        value = data.get(el)
        if value is not None:
            shift.__setattr__(el, value)

    return shift


async def get_operator_id(state: FSMContext) -> int | None:
    data = await state.get_data()

    return data.get("operator_id")


async def get_operator_name(state: FSMContext) -> str | None:
    data = await state.get_data()
    return data.get("operator_name")
