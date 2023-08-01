from typing import Sequence

from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.core.filters.admin import isAdminCB
from app.core.filters.operator import isOperatorCB
from app.core.keyboards.admin.menu import get_admin_menu_keyboard
from app.core.keyboards.base import get_cancel_keyboard
from app.core.keyboards.menu import MenuCB, MenuTarget, send_menu_keyboard
from app.core.keyboards.operator.menu import send_operator_menu_keyboard
from app.core.states.admin import AdminMenu
from app.core.states.feedback import FeedbackMenu
from app.services.database.dao.cleaning import CleaningDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.user import Role
from app.services.notifier.cleaning import CleaningNotifier

menu_router = Router(name="menu-router")


@menu_router.message(Command(commands=["start"]))
async def cmd_start(
    message: types.Message, state: FSMContext, session: async_sessionmaker[AsyncSession]
):
    await state.clear()
    userdao = UserDAO(session=session)
    if not await userdao.exists(chat_id=message.chat.id):
        await message.answer(
            text=(
                "Вас не добавили в список пользователей\\."
                "Пожалуйста напишите команду /id и отправьте свой id администратору"
            )
        )
        return

    user = await userdao.get_by_id(id_=message.chat.id)
    roles: Sequence[Role] = await userdao.get_user_roles(user)  # type: ignore
    if len(roles) == 0:
        await message.answer("Для вас не неназначено ни одной роли")
        return

    await send_menu_keyboard(message.answer, message, state, session)


@menu_router.callback_query(
    MenuCB.filter(F.target == MenuTarget.OPERATOR_MENU),
    isOperatorCB(),
)
async def cb_open_operator_menu(
    cb: types.CallbackQuery, state: FSMContext, session: async_sessionmaker
) -> None:
    await cb.answer()
    await send_operator_menu_keyboard(cb.message.edit_text, state, session)  # type: ignore


@menu_router.callback_query(
    MenuCB.filter(F.target == MenuTarget.MODERATOR_MENU),
)
async def cb_open_moderator_menu(cb: types.CallbackQuery) -> None:
    await cb.answer(text="В разработке", show_alert=True)


@menu_router.callback_query(
    MenuCB.filter(F.target == MenuTarget.ADMIN_MENU),
    isAdminCB(),
)
async def cb_open_admin_menu(
    cb: types.CallbackQuery,
    state: FSMContext,
) -> None:
    await cb.answer()

    await state.set_state(AdminMenu.menu)
    await cb.message.edit_text("Админ меню", reply_markup=get_admin_menu_keyboard())  # type: ignore


@menu_router.callback_query(MenuCB.filter(F.target == MenuTarget.FEEDBACK_MENU))
async def cb_open_feedback_menu(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()

    await state.set_state(FeedbackMenu.get_feedback)
    await cb.message.edit_text(  # type: ignore
        "Напишите сообщение, которые вы хотите передать администраторам мойки\\. Вы также можете прикрепить до 10 фотографий",
        reply_markup=get_cancel_keyboard(),
    )
