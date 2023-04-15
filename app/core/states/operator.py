from aiogram.fsm.state import StatesGroup, State


class OperatorMenu(StatesGroup):
    menu = State()

    class ManualStartSection(StatesGroup):
        menu = State()

        class ManualStartReport(StatesGroup):
            type = State()

            class TestManualStart(StatesGroup):
                description = State()

            class ServiceManualStart(StatesGroup):
                description = State()

            class RewashManualStart(StatesGroup):
                photo = State()
                description = State()

            class PaidManualStart(StatesGroup):
                payment_method = State()
                payment_amount = State()

    ...
