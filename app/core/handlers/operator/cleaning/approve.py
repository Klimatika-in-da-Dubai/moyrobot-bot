from sys import call_tracing
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action

from app.core.keyboards.operator.cleaning.approve import (
    CleaningApproveCB,
    CleaningApproveTarget,
)
from app.services.database.dao.cleaning import CleaningDAO
from app.services.database.models.cleaning import Cleaning


approve_router = Router()


@approve_router.callback_query(CleaningApproveCB.filter((F.action == Action.SELECT)))
async def cb_check_cleaning(
    cb: types.CallbackQuery,
    callback_data: CleaningApproveCB,
    session: async_sessionmaker,
):
    if await is_checked(callback_data.cleaning_id, session):
        cb.answer("Отчёт о уборке уже был проверен", show_alert=True)
        await edit_cleaning_message(cb, callback_data.cleaning_id, session)
        return
    approve_value = get_approve_value(callback_data)
    cleaningdao = CleaningDAO(session)
    cb.answer()
    await cleaningdao.set_approved_by_id(callback_data.cleaning_id, approve_value)
    await edit_cleaning_message(cb, callback_data.cleaning_id, session)


def get_approve_value(cleaning_cb: CleaningApproveCB):
    if cleaning_cb.target == CleaningApproveTarget.DECLINE:
        return False
    return True


async def is_checked(cleaning_id: int, session: async_sessionmaker):
    cleaningdao = CleaningDAO(session)
    cleaning: Cleaning = await cleaningdao.get_by_id(cleaning_id)  # type: ignore
    return cleaning.approved is not None


async def edit_cleaning_message(
    cb: types.CallbackQuery, cleaning_id: int, session: async_sessionmaker
):
    cleaningdao = CleaningDAO(session)
    cleaning: Cleaning = await cleaningdao.get_by_id(cleaning_id)  # type: ignore

    if cleaning.approved is True:
        await cb.message.edit_text("Получен отчёт об уборке\n*Статус:* Принят ✅")  # type: ignore
    else:
        await cb.message.edit_text("Получен отчёт об уборке\n*Статус:* Отклонён ❌")  # type: ignore
