from aiogram.fsm.state import State, StatesGroup


class OperatorRequestMenu(StatesGroup):
    get_operator_request = State()
