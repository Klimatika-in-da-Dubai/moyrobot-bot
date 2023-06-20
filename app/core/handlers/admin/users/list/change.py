from typing import Any
from aiogram import Router, types, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.users.list.change import (
    ChangeUserCB,
    ChangeUserTarget,
    get_roles_keyboard,
    send_change_user_menu,
)
from app.core.keyboards.admin.users.list.selected_user import send_selected_user_menu
from app.core.keyboards.admin.users.mailing import send_mailing_selection

from app.core.states.admin import AdminMenu
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard


from app.services.database.dao.mailing import MailingDAO
from app.services.database.dao.salary import SalaryDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.mailing import Mailing
from app.services.database.models.salary import Salary
from app.services.database.models.user import Role, User, UserRole

change_user_router = Router()


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.menu,
    isAdminCB(),
    ChangeUserCB.filter(
        (F.target == ChangeUserTarget.ID) & (F.action == Action.ENTER_TEXT)
    ),
)
async def cb_enter_id(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.Users.List.Selected.Change.id)
    await cb.message.answer("Введите id пользователя")  # type: ignore


@change_user_router.message(AdminMenu.Users.List.Selected.Change.id, F.text)
async def message_user_id(message: types.Message, state: FSMContext):
    if not message.text.isnumeric():  # type: ignore
        await message.answer("Введите число")
        return
    await state.update_data(id=int(message.text))  # type: ignore
    await send_change_user_menu(message.answer, state)


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.menu,
    isAdminCB(),
    ChangeUserCB.filter(
        (F.target == ChangeUserTarget.NAME) & (F.action == Action.ENTER_TEXT)
    ),
)
async def cb_enter_name(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.Users.List.Selected.Change.name)
    await cb.message.answer("Введите имя пользователя")  # type: ignore


@change_user_router.message(AdminMenu.Users.List.Selected.Change.name, F.text)
async def message_user_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await send_change_user_menu(message.answer, state)


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.menu,
    isAdminCB(),
    ChangeUserCB.filter(
        (F.target == ChangeUserTarget.SALARY) & (F.action == Action.ENTER_TEXT)
    ),
)
async def cb_enter_salary(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.Users.List.Selected.Change.salary)
    await cb.message.edit_text(  # type: ignore
        text="Введите зарплату за смену для работника",
        reply_markup=get_cancel_keyboard(),
    )


@change_user_router.message(AdminMenu.Users.List.Selected.Change.salary, F.text)
async def message_salary(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Нет текста в сообщении")
        return

    if not message.text.isnumeric():
        await message.edit_text(
            text="Введите число", reply_markup=get_cancel_keyboard()
        )
        return

    if int(message.text) < 0:
        await message.edit_text(
            text="Зарплата не может быть отрицательной",
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(salary=int(message.text))
    await send_change_user_menu(message.answer, state)


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.menu,
    isAdminCB(),
    ChangeUserCB.filter(
        (F.target == ChangeUserTarget.MAILING) & (F.action == Action.OPEN)
    ),
)
async def cb_open_mailing_selection(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    if data.get("mailings") is None:
        await state.update_data(mailings=[])
    await send_mailing_selection(cb.message.edit_text, state)  # type: ignore


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.menu,
    isAdminCB(),
    ChangeUserCB.filter(
        (F.target == ChangeUserTarget.ROLES) & (F.action == Action.OPEN)
    ),
)
async def cb_open_role_selection(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminMenu.Users.List.Selected.Change.role)
    await cb.message.edit_text(  # type: ignore
        "Выберете роли пользователя", reply_markup=await get_roles_keyboard(state)
    )


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.role,
    isAdminCB(),
    ChangeUserCB.filter(F.action == Action.SELECT),
)
async def cb_select_role(
    cb: types.CallbackQuery, state: FSMContext, callback_data: ChangeUserCB
):
    await cb.answer()

    data = await state.get_data()
    if data.get("roles") is None:
        await state.update_data(roles=list())

    roles: list[Role] = (await state.get_data()).get("roles")  # type: ignore
    selected_role = None
    match callback_data.target:
        case ChangeUserTarget.OPERATOR_ROLE:
            selected_role = Role.OPERATOR
        case ChangeUserTarget.MODERATOR_ROLE:
            selected_role = Role.MODERATOR
        case ChangeUserTarget.ADMIN_ROLE:
            selected_role = Role.ADMIN

    if selected_role is None:
        await cb.message.edit_text("Выберете роли пользователя", reply_markup=await get_roles_keyboard(state))  # type: ignore
        return

    if selected_role in roles:
        roles.remove(selected_role)
    else:
        roles.append(selected_role)

    await state.update_data(roles=roles)

    await cb.message.edit_text("Выберете роли пользователя", reply_markup=await get_roles_keyboard(state))  # type: ignore


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.role,
    isAdminCB(),
    ChangeUserCB.filter(F.action == Action.BACK),
)
async def cb_roles_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_change_user_menu(cb.message.edit_text, state)  # type: ignore


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.menu,
    isAdminCB(),
    ChangeUserCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_selected_user_menu(cb.message.edit_text, state, session)  # type: ignore


@change_user_router.callback_query(
    or_f(AdminMenu.Users.List.Selected.Change.salary),
    isAdminCB(),
    CancelCB.filter(F.action == Action.CANCEL),
)
async def cb_cancel(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_change_user_menu(cb.message.edit_text, state)  # type: ignore


@change_user_router.callback_query(
    AdminMenu.Users.List.Selected.Change.menu,
    isAdminCB(),
    ChangeUserCB.filter(F.action == Action.ENTER),
)
async def cb_enter(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
):
    data = await state.get_data()
    if not is_correct_data(data):
        await cb.answer(text="Не все поля заполнены", show_alert=True)
        return

    id = data.get("id")
    user = User(id=id, name=data.get("name"))
    user_roles = [UserRole(id=id, role=role) for role in data.get("roles")]  # type: ignore
    mailings = [Mailing(id=id, type=mailing_type) for mailing_type in data.get("mailings")]  # type: ignore
    salary = Salary(user_id=id, salary=data.get("salary"))

    userdao = UserDAO(session=session)
    mailingdao = MailingDAO(session=session)
    salarydao = SalaryDAO(session=session)
    await userdao.add_user_with_roles(user, user_roles)

    await salarydao.add_salary(salary)
    for mailing in mailings:
        await mailingdao.add_mailing(mailing)

    await cb_back(cb, state)


def is_correct_data(data: dict[str, Any]):
    id = data.get("id")
    name = data.get("name")
    roles = data.get("roles")
    salary = data.get("salary")

    if id is None or id == "":
        return False
    if name is None or name == "":
        return False
    if roles is None or len(roles) == 0:
        return False
    if salary is None:
        return False
    return True
