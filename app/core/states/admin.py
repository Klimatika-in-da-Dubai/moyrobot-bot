from aiogram.fsm.state import StatesGroup, State


class AdminMenu(StatesGroup):
    menu = State()

    class Operators(StatesGroup):
        ...

    class Moderators(StatesGroup):
        ...

    # Нужно ли?
    class Admins(StatesGroup):
        ...

    class Users(StatesGroup):
        menu = State()

        class Add(StatesGroup):
            menu = State()
            id = State()
            name = State()
            salary = State()
            mailing = State()
            role = State()

        class List(StatesGroup):
            menu = State()

            class Selected(StatesGroup):
                menu = State()
                delete = State()

                class Change(StatesGroup):
                    menu = State()
                    id = State()
                    name = State()
                    salary = State()
                    mailing = State()
                    role = State()

    class Groups(StatesGroup):
        menu = State()

        class Selected(StatesGroup):
            menu = State()
            mailing = State()
            delete = State()

    class MoneyCollection(StatesGroup):
        money_collection = State()

    class CashboxReplenishment(StatesGroup):
        cashbox_replenishment = State()
