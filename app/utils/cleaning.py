from aiogram.fsm.context import FSMContext

from app.services.database.dto.cleaning import CleaningDTO, Place, Work


async def get_place_id(state: FSMContext) -> int:
    data = await state.get_data()
    place_id = data.get("place_id")
    if place_id is None:
        raise ValueError("no place_id in state")

    return place_id


async def get_work_id(state: FSMContext) -> int:
    data = await state.get_data()
    work_id = data.get("work_id")
    if work_id is None:
        raise ValueError("no work_id in state")

    return work_id


async def get_current_place(state: FSMContext) -> Place:
    data = await state.get_data()
    cleaning = CleaningDTO.from_dict(data)
    place_id = await get_place_id(state)
    return cleaning.places[place_id]


async def get_current_work(state: FSMContext) -> Work:
    data = await state.get_data()
    cleaning = CleaningDTO.from_dict(data)
    place_id = await get_place_id(state)
    work_id = await get_work_id(state)
    return cleaning.places[place_id].works[work_id]
