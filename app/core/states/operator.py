from aiogram.fsm.state import StatesGroup, State


class OperatorMenu(StatesGroup):
    menu = State()

    class Shift(StatesGroup):
        menu = State()
        operator = State()
        auth = State()
        money_amount = State()
        antifreeze_count = State()
        robot_check = State()

        class Chemistry(StatesGroup):
            menu = State()
            shampoo = State()
            foam = State()
            wax = State()

    class ManualStart(StatesGroup):
        menu = State()
        type = State()

        class TestManualStart(StatesGroup):
            menu = State()
            photo = State()
            description = State()

        class ServiceManualStart(StatesGroup):
            menu = State()
            photo = State()
            description = State()

        class RewashManualStart(StatesGroup):
            menu = State()
            photo = State()
            description = State()

        class PaidManualStart(StatesGroup):
            menu = State()
            payment_method = State()
            payment_amount = State()
            photo = State()
            bonus = State()

        class CorporateManualStart(StatesGroup):
            menu = State()
            photo = State()
            description = State()
            corporation = State()

    class Cleaning(StatesGroup):
        menu = State()

        class Place(StatesGroup):
            menu = State()

            class Work(StatesGroup):
                menu = State()
                photo = State()

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
