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


async def is_cleaning_exists(state: FSMContext) -> bool:
    data = await state.get_data()
    return data.get("cleaning") is not None


async def add_cleaning_to_state(state: FSMContext) -> None:
    cleaning = CleaningDTO(
        places=[
            Place(
                name="Бокс 1",
                works=[
                    Work(name="По направлению движения"),
                    Work(name="Против направления движения"),
                ],
            ),
            Place(
                name="Бокс 2",
                works=[
                    Work(name="По направлению движения"),
                    Work(name="Против направления движения"),
                ],
            ),
            Place(
                name="Территория 1",
                works=[
                    Work(name="Территория у ворот"),
                    Work(name="Асфальт у бокса 1"),
                    Work(name="Асфальт у бокса 2"),
                ],
            ),
            Place(
                name="Территория 2",
                works=[
                    Work(name="Пылесос"),
                    # Work(name="Мойка ковров"),
                    # Work(name="Уровень шампуня для мойки ковров"),
                    Work(name="Фото салфеток (внутри)"),
                ],
            ),
            Place(
                name="Операторская",
                works=[
                    Work(name="Общее фото помещения"),
                    Work(name="Фото стола"),
                ],
            ),
            Place(
                name="Техническое помещение",
                works=[
                    Work(name="Шкаф доз 1"),
                    Work(name="Шкаф доз 2"),
                    Work(name="Общее фото"),
                ],
            ),
        ]
    )
    await state.update_data(cleaning=cleaning.to_dict())
