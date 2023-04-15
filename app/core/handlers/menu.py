from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.core.filters.admin import isAdminCB
from app.core.filters.operator import isOperatorCB

from app.core.states.operator import OperatorMenu
from app.core.states.admin import AdminMenu
from app.core.keyboards.base import Action
from app.core.keyboards.menu import get_menu_keyboard, MenuCB
from app.core.keyboards.admin.menu import get_admin_menu_keyboard
from app.core.keyboards.operator.menu import get_operator_menu_keyboard
from app.services.database.dao.user import UserDAO
from app.services.database.models.user import Role, User

menu_router = Router()


@menu_router.message(Command(commands=["start"]))
async def cmd_start(
    message: types.Message, state: FSMContext, session: async_sessionmaker[AsyncSession]
):
    await state.clear()
    userdao = UserDAO(session=session)
    if not await userdao.exists(chat_id=message.chat.id):
        await message.answer(
            "Вас не добавили в список пользователей\. Пожалуйста напишите команду /id и отправьте свой id администратору"
        )
        return

    user: User = await userdao.get_by_id(id_=message.chat.id)
    roles: list[Role] = await userdao.get_user_roles(user)
    if len(roles) == 0:
        await message.answer("Для вас не неназначено ни одной роли")
        return

    await message.answer(
        f"Добро пожаловать, {user.name}",
        reply_markup=await get_menu_keyboard(message.chat.id, session),
    )


@menu_router.callback_query(
    isOperatorCB(), MenuCB.filter((F.role == Role.OPERATOR) & (F.action == Action.OPEN))
)
async def cb_open_operator_menu(cb: types.CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(OperatorMenu.menu)
    await cb.message.edit_text(  # type: ignore
        "Меню оператора", reply_markup=get_operator_menu_keyboard()
    )
    ...


@menu_router.callback_query(
    MenuCB.filter((F.role == Role.MODERATOR) & (F.action == Action.OPEN))
)
async def cb_open_moderator_menu(cb: types.CallbackQuery, state: FSMContext) -> None:
    await cb.answer(text="В разработке", show_alert=True)
    ...


@menu_router.callback_query(
    isAdminCB(), MenuCB.filter((F.role == Role.ADMIN) & (F.action == Action.OPEN))
)
async def cb_open_admin_menu(
    cb: types.CallbackQuery,
    state: FSMContext,
    session: async_sessionmaker[AsyncSession],
) -> None:
    await cb.answer()

    await state.set_state(AdminMenu.menu)
    await cb.message.edit_text(  # type: ignore
        "Админ меню", reply_markup=get_admin_menu_keyboard()
    )


@menu_router.message(Command(commands=["id"]))
async def cmd_id(message: types.Message) -> None:
    await message.answer(f"Ваш id: *`{message.chat.id}`*")
