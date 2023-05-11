from aiogram.fsm.state import StatesGroup, State


class OperatorMenu(StatesGroup):
    menu = State()

    class Shift(StatesGroup):
        menu = State()
        operator_name = State()
        money_amount = State()
        antifreeze_count = State()
        chemistry_count = State()
        robot_check = State()

    class ManualStart(StatesGroup):
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

    class Promocode(StatesGroup):
        menu = State()
        phone = State()
        wash_mode = State()
        description = State()

    class Bonus(StatesGroup):
        menu = State()
        phone = State()
        bonus_amount = State()
        description = State()

    class Refund(StatesGroup):
        menu = State()
        description = State()
        statement_photo = State()
        consumable_photo = State()

    class Antifreeze(StatesGroup):
        menu = State()
        payment_method = State()
        payment_amount = State()
