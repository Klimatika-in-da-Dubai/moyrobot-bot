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


approve_router = Router()


@approve_router.callback_query(
    CleaningApproveCB.filter(
        (F.action == Action.SELECT) & (F.target == CleaningApproveTarget.DECLINE)
    )
)
async def cb_decline(
    cb: types.CallbackQuery,
    callback_data: CleaningApproveCB,
    session: async_sessionmaker,
):
    cb.answer()
    cleaningdao = CleaningDAO(session)
    await cleaningdao.set_approved_by_id(callback_data.cleaning_id, False)
    await cb.message.edit_text("Получен отчёт об уборке\n*Статус:* Отклонён ❌")  # type: ignore


@approve_router.callback_query(
    CleaningApproveCB.filter(
        (F.action == Action.SELECT) & (F.target == CleaningApproveTarget.APPROVE)
    )
)
async def cb_approve(
    cb: types.CallbackQuery,
    callback_data: CleaningApproveCB,
    session: async_sessionmaker,
):
    cb.answer()
    cleaningdao = CleaningDAO(session)
    await cleaningdao.set_approved_by_id(callback_data.cleaning_id, True)
    await cb.message.edit_text("Получен отчёт об уборке\n*Статус:* Принят ✅")  # type: ignore
