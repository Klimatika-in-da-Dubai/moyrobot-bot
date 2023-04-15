from aiogram.fsm.state import StatesGroup, State


class OperatorMenu(StatesGroup):
    menu = State()

    class ManualStartSection(StatesGroup):
        menu = State()

    ...
