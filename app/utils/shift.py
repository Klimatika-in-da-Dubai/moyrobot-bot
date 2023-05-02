from aiogram.fsm.context import FSMContext

from app.services.database.models.shift import CloseShift, OpenShift


async def get_open_shift(state: FSMContext) -> OpenShift:
    data = await state.get_data()

    shift = OpenShift()

    columns = [
        "money_amount",
        "antifreeze_count",
        "chemistry_count",
        "chemistry_check",
        "equipment_check",
        "robot_movement_check",
        "robot_leak_check",
        "gates_check",
        "cleaning_check",
    ]

    for el in columns:
        value = data.get(el)
        if value is not None:
            shift.__setattr__(el, value)

    return shift


async def get_close_shift(state: FSMContext) -> CloseShift:
    data = await state.get_data()

    shift = CloseShift()

    columns = [
        "money_amount",
        "antifreeze_count",
        "chemistry_count",
        "chemistry_check",
        "equipment_check",
        "robot_movement_check",
        "robot_leak_check",
        "gates_check",
    ]

    for el in columns:
        value = data.get(el)
        if value is not None:
            shift.__setattr__(el, value)

    return shift
