from aiogram.fsm.state import StatesGroup, State


class OperatorMenu(StatesGroup):
    menu = State()

    class ManualStartSection(StatesGroup):
        menu = State()
        type = State()

        class TestManualStart(StatesGroup):
            menu = State()
            description = State()

        class ServiceManualStart(StatesGroup):
            menu = State()
            description = State()

        class RewashManualStart(StatesGroup):
            menu = State()
            photo = State()
            description = State()

        class PaidManualStart(StatesGroup):
            menu = State()
            payment_method = State()
            payment_amount = State()
            bonus = State()

    ...
