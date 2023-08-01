from aiogram.fsm.state import State, StatesGroup


class FeedbackMenu(StatesGroup):
    get_feedback = State()
