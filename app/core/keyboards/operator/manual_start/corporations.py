from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.job import Iterable
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.base import Action
from app.core.states.operator import OperatorMenu
from app.services.database.dao.corporation import CorporationDAO
from app.services.database.models.corporation import Corporation


class CorporationsMenuCB(CallbackData, prefix="corporations_menu"):
    action: Action
    corporation_id: int


def get_corporations_menu(corporations: Iterable[Corporation]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for corporation in corporations:
        builder.row(
            types.InlineKeyboardButton(
                text=corporation.name,
                callback_data=CorporationsMenuCB(
                    action=Action.SELECT, corporation_id=corporation.id
                ).pack(),
            )
        )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=CorporationsMenuCB(
                action=Action.BACK, corporation_id=-1
            ).pack(),
        )
    )
    return builder.as_markup()


async def send_corporations_menu(func, state: FSMContext, session: async_sessionmaker):
    corporations = await CorporationDAO(session).get_all()
    await state.set_state(OperatorMenu.ManualStart.CorporateManualStart.corporation)
    await func("Выберете компанию", reply_markup=get_corporations_menu(corporations))
