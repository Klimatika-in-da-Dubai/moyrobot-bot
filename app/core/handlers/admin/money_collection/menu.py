from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.menu import get_admin_menu_keyboard
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard

from app.core.states.admin import AdminMenu
from app.services.database.dao.money_collection import MoneyCollectionDAO
from app.services.database.models.money_collection import MoneyCollection


menu_router = Router()


@menu_router.message(AdminMenu.MoneyCollection.money_collection, F.text)
async def message_money_collection(
    message: types.Message, state: FSMContext, session: async_sessionmaker
):
    text: str = message.text  # type: ignore

    if not text.isnumeric():
        await message.answer("Введите число", reply_markup=get_cancel_keyboard())
        return

    money_count: int = int(text)  # type; ignore
    if money_count <= 0:
        await message.answer("Инкассация не может быть <= 0")
        return

    money_collection = MoneyCollection(money_amount=money_count)
    money_collectiondao = MoneyCollectionDAO(session)
    await money_collectiondao.add_money_collection(money_collection)

    await state.set_state(AdminMenu.menu)
    await message.answer(  # type: ignore
        text="Админ меню", reply_markup=get_admin_menu_keyboard()
    )


@menu_router.callback_query(
    AdminMenu.MoneyCollection.money_collection,
    isAdminCB(),
    CancelCB.filter((F.action == Action.CANCEL)),
)
async def cb_cancel(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.menu)
    await cb.message.edit_text(  # type: ignore
        text="Админ меню", reply_markup=get_admin_menu_keyboard()
    )
