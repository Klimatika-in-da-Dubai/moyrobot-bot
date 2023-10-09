from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards.notifications.consumable_request import (
    ConsumableRequestNotifyCB,
    get_consumable_given_keyboard,
)
from app.services.database.dao.consumable_request import ConsumableRequestDAO
from app.services.database.models.consumable_request import ConsumableRequest


consumable_request_router = Router()


@consumable_request_router.callback_query(ConsumableRequestNotifyCB.filter())
async def cb_consumable_request_notify_check(
    cb: CallbackQuery,
    bot: Bot,
    callback_data: ConsumableRequestNotifyCB,
    session: AsyncSession,
):
    consumable_request_dao = ConsumableRequestDAO(session)
    consumable_request = await consumable_request_dao.get_by_id(
        id_=callback_data.consumable_request_id
    )
    if consumable_request is None:
        await cb.answer("Произошла ошибка в базе данных", show_alert=True)
        return

    if consumable_request.satisfied is True:
        await cb.answer("Сообщение уже было рассмотренно", show_alert=True)
        return

    await cb.answer()

    await consumable_request_dao.make_satisfied(consumable_request)
    await edit_notifies(bot, consumable_request)


async def edit_notifies(bot: Bot, consumable_request: ConsumableRequest):
    for el in consumable_request.notify_messages_ids:
        chat_id = el.get("chat_id")
        message_id = el.get("message_id")
        await bot.edit_message_reply_markup(
            chat_id, message_id, reply_markup=get_consumable_given_keyboard()
        )
