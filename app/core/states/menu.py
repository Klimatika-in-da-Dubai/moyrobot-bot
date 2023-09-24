from aiogram.fsm.state import StatesGroup, State


class MainMenu(StatesGroup):
    menu = State()
    operator_request = State()
