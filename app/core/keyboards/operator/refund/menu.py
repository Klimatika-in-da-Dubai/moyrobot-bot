from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.base import Action
from app.core.keyboards.operator.refund.base import (
    RefundEmojis,
    RefundMenuCB,
    RefundMenuTarget,
    get_refund_base_builder,
    get_refund_emojis,
)
from app.core.states.operator import OperatorMenu
from app.services.database.models.refund import PaymentDevice, Refund
from app.services.database.models.utils import PaymentMethod
from app.utils.refund import get_refund, get_refund_menu_text


async def get_default_refund_keyboard(
    refund: Refund, state: FSMContext
) -> types.InlineKeyboardMarkup:
    builder = await get_refund_base_builder(refund, state)

    emojis: RefundEmojis = await get_refund_emojis(refund, state)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Причина {emojis.description}",
            callback_data=RefundMenuCB(
                action=Action.ENTER_TEXT, target=RefundMenuTarget.DESCRIPTION
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Фото заявления {emojis.statement_photo}",
            callback_data=RefundMenuCB(
                action=Action.ADD_PHOTO, target=RefundMenuTarget.STATEMENT_PHOTO
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Фото расходника {emojis.consumable_photo}",
            callback_data=RefundMenuCB(
                action=Action.ADD_PHOTO, target=RefundMenuTarget.CONSUMABLE_PHOTO
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Выдайте нужную сумму из кассы {emojis.give_money}",
            callback_data=RefundMenuCB(
                action=Action.SELECT, target=RefundMenuTarget.GIVE_MONEY
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=RefundMenuCB(
                action=Action.BACK, target=RefundMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=RefundMenuCB(
                action=Action.ENTER, target=RefundMenuTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


async def get_terminal_card_refund_keyboard(
    refund: Refund, state: FSMContext
) -> types.InlineKeyboardMarkup:
    builder = await get_refund_base_builder(refund, state)

    emojis: RefundEmojis = await get_refund_emojis(refund, state)

    builder.row(
        types.InlineKeyboardButton(
            text=f"Причина {emojis.description}",
            callback_data=RefundMenuCB(
                action=Action.ENTER_TEXT, target=RefundMenuTarget.DESCRIPTION
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Фото заявления {emojis.statement_photo}",
            callback_data=RefundMenuCB(
                action=Action.ADD_PHOTO, target=RefundMenuTarget.STATEMENT_PHOTO
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text=f"Средства вернуться на карту {emojis.money_on_card}",
            callback_data=RefundMenuCB(
                action=Action.SELECT, target=RefundMenuTarget.MONEY_ON_CARD
            ).pack(),
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=RefundMenuCB(
                action=Action.BACK, target=RefundMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text="Готово",
            callback_data=RefundMenuCB(
                action=Action.ENTER, target=RefundMenuTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


async def send_refund_keyboard(func, state: FSMContext, session: AsyncSession):
    refund: Refund = await get_refund(state)

    if (
        refund.payment_device == PaymentDevice.TERMINAL
        and refund.payment_method == PaymentMethod.CARD
    ):
        reply_markup = await get_terminal_card_refund_keyboard(refund, state)
    else:
        reply_markup = await get_default_refund_keyboard(refund, state)

    text = get_refund_menu_text(refund)
    await func(text=text, reply_markup=reply_markup)
    await state.set_state(OperatorMenu.Refund.menu)
