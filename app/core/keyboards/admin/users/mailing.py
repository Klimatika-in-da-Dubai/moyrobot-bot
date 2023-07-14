from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Literal
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from app.core.keyboards.base import Action
from app.core.states.admin import AdminMenu
from app.services.database.models.mailing import MailingType


class MailingSelectionCB(CallbackData, prefix="mailing_selection"):
    action: Action
    mailing: MailingType


@dataclass
class MailingEmojis:
    monthly_report: Literal["✅", "❌"]
    manual_start_report_alert: Literal["✅", "❌"]
    manual_start_report_remind: Literal["✅", "❌"]
    manual_start: Literal["✅", "❌"]
    shift: Literal["✅", "❌"]
    shift_check: Literal["✅", "❌"]
    shift_difference: Literal["✅", "❌"]
    antifreeze: Literal["✅", "❌"]
    cleaning: Literal["✅", "❌"]
    promocode: Literal["✅", "❌"]
    bonus: Literal["✅", "❌"]
    refund: Literal["✅", "❌"]


@dataclass
class ButtonInfo:
    description: str
    mailing_type: MailingType
    mailing_emoji: Literal["✅", "❌"]


async def get_mailing_selection_keyboard(
    state: FSMContext,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = await get_mailing_buttons(state)
    for button in buttons:
        builder.row(
            types.InlineKeyboardButton(
                text=f"{button.description} {button.mailing_emoji}",
                callback_data=MailingSelectionCB(
                    action=Action.SELECT, mailing=button.mailing_type
                ).pack(),
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=MailingSelectionCB(
                action=Action.ENTER,
                mailing=MailingType.REFUND,  # mailing_type have no sense for that button
            ).pack(),
        )
    )
    return builder.as_markup()


async def get_mailing_buttons(state: FSMContext) -> list[ButtonInfo]:
    return [
        ButtonInfo(
            description="Месячный отчёт",
            mailing_type=MailingType.MONTHLY_REPORT,
            mailing_emoji=await get_mailing_emoji(state, MailingType.MONTHLY_REPORT),
        ),
        ButtonInfo(
            description="Ручной запуск тревога",
            mailing_type=MailingType.MANUAL_START_REPORT_ALERT,
            mailing_emoji=await get_mailing_emoji(
                state, MailingType.MANUAL_START_REPORT_ALERT
            ),
        ),
        ButtonInfo(
            description="Ручной запуск напоминание",
            mailing_type=MailingType.MANUAL_START_REPORT_REMIND,
            mailing_emoji=await get_mailing_emoji(
                state, MailingType.MANUAL_START_REPORT_REMIND
            ),
        ),
        ButtonInfo(
            description="Ручной запуск отчёт",
            mailing_type=MailingType.MANUAL_START,
            mailing_emoji=await get_mailing_emoji(state, MailingType.MANUAL_START),
        ),
        ButtonInfo(
            description="Отчёт смены",
            mailing_type=MailingType.SHIFT,
            mailing_emoji=await get_mailing_emoji(state, MailingType.SHIFT),
        ),
        ButtonInfo(
            description="Покупка антифриза",
            mailing_type=MailingType.ANTIFREEZE,
            mailing_emoji=await get_mailing_emoji(state, MailingType.ANTIFREEZE),
        ),
        ButtonInfo(
            description="Отчёт об уборке",
            mailing_type=MailingType.CLEANING,
            mailing_emoji=await get_mailing_emoji(state, MailingType.CLEANING),
        ),
        ButtonInfo(
            description="Выдача промокода",
            mailing_type=MailingType.PROMOCODE,
            mailing_emoji=await get_mailing_emoji(state, MailingType.PROMOCODE),
        ),
        ButtonInfo(
            description="Недельная рассылка промокодов",
            mailing_type=MailingType.PROMOCODE_CHECK,
            mailing_emoji=await get_mailing_emoji(state, MailingType.PROMOCODE_CHECK),
        ),
        ButtonInfo(
            description="Выдача бонуса",
            mailing_type=MailingType.BONUS,
            mailing_emoji=await get_mailing_emoji(state, MailingType.BONUS),
        ),
        ButtonInfo(
            description="Недельная рассылка бонусов",
            mailing_type=MailingType.BONUS_CHECK,
            mailing_emoji=await get_mailing_emoji(state, MailingType.BONUS_CHECK),
        ),
        ButtonInfo(
            description="Отчёт о возврате",
            mailing_type=MailingType.REFUND,
            mailing_emoji=await get_mailing_emoji(state, MailingType.REFUND),
        ),
        ButtonInfo(
            description="Проверка оплаты картой",
            mailing_type=MailingType.PAYMENT_CHECK,
            mailing_emoji=await get_mailing_emoji(state, MailingType.PAYMENT_CHECK),
        ),
        ButtonInfo(
            description="Проверка оплаты картой тревога",
            mailing_type=MailingType.PAYMENT_CHECK_ALERT,
            mailing_emoji=await get_mailing_emoji(
                state, MailingType.PAYMENT_CHECK_ALERT
            ),
        ),
    ]


async def get_mailing_emoji(
    state: FSMContext, mailing_type: MailingType
) -> Literal["✅", "❌"]:
    data = await state.get_data()
    if mailing_type in data["mailings"]:
        return "✅"
    return "❌"


async def send_mailing_selection(func, state: FSMContext):
    await state.set_state(AdminMenu.Users.Add.mailing)
    await func(
        text="Выберете рассыли",
        reply_markup=await get_mailing_selection_keyboard(state),
    )
