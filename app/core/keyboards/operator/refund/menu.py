from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.keyboards.base import Action
from app.core.keyboards.operator.refund.base import (
    RefundEmojis,
    RefundMenuCB,
    RefundMenuTarget,
    get_refund_base_builder,
)
from app.services.database.models.utils import PaymentMethod


def get_default_refund_keyboard(refund: Refund) -> types.InlineKeyboardMarkup:
    builder = get_refund_base_builder()

    refund_text_info = get_refund_text(refund)
    emojis: RefundEmojis = get_refund_emojis(refund)

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
            text=f"Назад",
            callback_data=RefundMenuCB(
                action=Action.BACK, target=RefundMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text=f"Готово",
            callback_data=RefundMenuCB(
                action=Action.ENTER, target=RefundMenuTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


def get_terminal_card_refund_keyboard(refund: Refund) -> types.InlineKeyboardMarkup:
    builder = get_refund_base_builder()

    refund_text_info = get_refund_text(refund)
    emojis: RefundEmojis = get_refund_emojis(refund)

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
            text=f"Назад",
            callback_data=RefundMenuCB(
                action=Action.BACK, target=RefundMenuTarget.NONE
            ).pack(),
        ),
        types.InlineKeyboardButton(
            text=f"Готово",
            callback_data=RefundMenuCB(
                action=Action.ENTER, target=RefundMenuTarget.NONE
            ).pack(),
        ),
    )

    return builder.as_markup()


async def send_refund_keyboard(func, state: FSMContext, session: async_sessionmaker):
    refund: Refund = get_refund(state)

    if (
        refund.payment_device == PaymentDevice.TERMINAL
        and refund.payment_method == PaymentMethod.CARD
    ):
        reply_markup = get_terminal_card_refund_keyboard(refund)
    else:
        reply_markup = get_default_refund_keyboard(refund)

    await func(text="Возврат", reply_markup=reply_markup)
