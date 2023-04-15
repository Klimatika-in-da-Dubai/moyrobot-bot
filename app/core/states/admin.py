from aiogram.fsm.state import StatesGroup, State


class AdminMenu(StatesGroup):
    menu = State()

    class OperatorsSection(StatesGroup):
        ...

    class ModeratorsSection(StatesGroup):
        ...

    # Нужно ли?
    class AdminsSection(StatesGroup):
        ...

    class UsersSection(StatesGroup):
        menu = State()

        class Add(StatesGroup):
            menu = State()
            id = State()
            name = State()
            role = State()
