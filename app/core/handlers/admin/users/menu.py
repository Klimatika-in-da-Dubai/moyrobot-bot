from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.core.filters.admin import isAdminCB


from app.core.states.admin import AdminMenu

from app.core.keyboards.base import Action
from app.core.keyboards.admin.menu import get_admin_menu_keyboard

from app.core.keyboards.admin.users.menu import UsersCB
from app.core.keyboards.admin.users.add import get_add_user_keyboard


menu_router = Router()


@menu_router.callback_query(
    AdminMenu.Users.menu,
    isAdminCB(),
    UsersCB.filter(F.action == Action.LIST),
)
async def cb_open_users_list(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer(text="В разработке", show_alert=True)
    ...


@menu_router.callback_query(
    AdminMenu.Users.menu,
    isAdminCB(),
    UsersCB.filter(F.action == Action.ADD),
)
async def cb_add_user(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.Users.Add.menu)
    await cb.message.edit_text(  # type: ignore
        text="Добавить пользователя", reply_markup=await get_add_user_keyboard(state)
    )


@menu_router.callback_query(
    AdminMenu.Users.menu,
    isAdminCB(),
    UsersCB.filter(F.action == Action.DELETE),
)
async def cb_delete_user(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer(text="В разработке", show_alert=True)
    ...


@menu_router.callback_query(
    AdminMenu.Users.menu,
    isAdminCB(),
    UsersCB.filter(F.action == Action.BACK),
)
async def cb_back(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.menu)
    await cb.message.edit_text(  # type: ignore
        text="Админ меню", reply_markup=get_admin_menu_keyboard()
    )
