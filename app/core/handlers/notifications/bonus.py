from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.base import Action

from app.core.keyboards.notifications.bonus import (
    BonusNotificationCB,
    BonusNotificationTarget,
    get_approve_keyboard,
    get_decline_keyboard,
    get_no_client_keyboard,
)
from app.services.client_database.dao.client_bonus import ClientBonusDAO
from app.services.database.dao.bonus import BonusDAO
from app.services.database.models.bonus import Bonus
from app.services.parser.terminal_session import NoClientError, TerminalSession


bonus_router = Router()


@bonus_router.callback_query(
    BonusNotificationCB.filter(
        (F.target == BonusNotificationTarget.APPROVE) & (F.action == Action.SELECT)
    )
)
async def cb_approve_bonus_check(
    cb: types.CallbackQuery,
    callback_data: BonusNotificationCB,
    session: AsyncSession,
    client_session: AsyncSession,
    terminal1: TerminalSession,
):
    bonus_dao = BonusDAO(session)
    bonus: Bonus | None = await bonus_dao.get_by_id(callback_data.id)
    if bonus is None:
        await cb.answer("Произошла ошибка в базе данных", show_alert=True)
        await cb.message.edit_reply_markup()  # type: ignore
        return

    try:
        async with terminal1 as terminal:
            await terminal.add_bonuses_by_phone(
                bonus.phone, bonus.bonus_amount, bonus.description
            )
    except NoClientError:
        await cb.answer("Нет клиента с таким номером телефона", show_alert=True)
        await bonus_dao.set_given(bonus, False)
        await cb.message.edit_reply_markup(reply_markup=get_no_client_keyboard())  # type: ignore
        return

    cb.answer()
    clientbonus_dao = ClientBonusDAO(client_session)
    await clientbonus_dao.add_bonuses(bonus.phone, bonus.bonus_amount)
    await bonus_dao.set_given(bonus, True)
    await cb.message.edit_reply_markup(reply_markup=get_approve_keyboard())  # type: ignore


@bonus_router.callback_query(
    BonusNotificationCB.filter(
        (F.target == BonusNotificationTarget.DECLINE) & (F.action == Action.SELECT)
    )
)
async def cb_decline_bonus_check(
    cb: types.CallbackQuery,
    callback_data: BonusNotificationCB,
    session: AsyncSession,
):
    cb.answer()
    bonus_dao = BonusDAO(session)
    bonus: Bonus | None = await bonus_dao.get_by_id(callback_data.id)
    if bonus is None:
        await cb.answer("Произошла ошибка в базе данных", show_alert=True)
        await cb.message.edit_reply_markup()  # type: ignore
        return
    await bonus_dao.set_given(bonus, False)
    await cb.message.edit_reply_markup(reply_markup=get_decline_keyboard())  # type: ignore
