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
            role = State()
