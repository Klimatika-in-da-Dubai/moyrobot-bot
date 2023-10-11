from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.filters.admin import isAdminCB
from app.core.keyboards.admin.menu import get_admin_menu_keyboard
from app.core.keyboards.base import Action, CancelCB, get_cancel_keyboard

from app.core.states.admin import AdminMenu
from app.services.database.dao.cashbox_replenishment import CashboxReplenishmentDAO
from app.services.database.models.cashbox_replenishment import CashboxReplenishment


menu_router = Router()


@menu_router.message(AdminMenu.CashboxReplenishment.cashbox_replenishment, F.text)
async def message_cashbox_replenishment(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    text: str = message.text  # type: ignore

    if not text.isnumeric():
        await message.answer("Введите число", reply_markup=get_cancel_keyboard())
        return

    money_count: int = int(text)  # type; ignore
    if money_count <= 0:
        await message.answer("Пополнение кассы не может быть <= 0")
        return

    cashbox_replenishment = CashboxReplenishment(money_amount=money_count)
    cashbox_replenishmentdao = CashboxReplenishmentDAO(session)
    await cashbox_replenishmentdao.add_cashbox_replenishment(cashbox_replenishment)

    await state.set_state(AdminMenu.menu)
    await message.answer(  # type: ignore
        text="Админ меню", reply_markup=get_admin_menu_keyboard()
    )


@menu_router.callback_query(
    AdminMenu.CashboxReplenishment.cashbox_replenishment,
    isAdminCB(),
    CancelCB.filter((F.action == Action.CANCEL)),
)
async def cb_cancel(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(AdminMenu.menu)
    await cb.message.edit_text(  # type: ignore
        text="Админ меню", reply_markup=get_admin_menu_keyboard()
    )
