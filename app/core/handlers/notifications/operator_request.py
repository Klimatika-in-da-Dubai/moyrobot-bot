from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.notifications.operator_request import (
    OperatorRequestNotifyCB,
    get_request_considered_keyboard,
)
from app.services.database.dao.operator_request import OperatorRequestDAO
from app.services.database.models.operator_request import OperatorRequest


operator_request_router = Router()


@operator_request_router.callback_query(OperatorRequestNotifyCB.filter())
async def cb_operator_request_notify_check(
    cb: CallbackQuery,
    bot: Bot,
    callback_data: OperatorRequestNotifyCB,
    session: async_sessionmaker,
):
    operator_request_dao = OperatorRequestDAO(session)
    operator_request = await operator_request_dao.get_by_id(
        id_=callback_data.operator_request_id
    )
    if operator_request is None:
        await cb.answer("Произошла ошибка в базе данных", show_alert=True)
        return

    if operator_request.satisfied is True:
        await cb.answer("Сообщение уже было рассмотренно", show_alert=True)
        return

    await cb.answer()

    await operator_request_dao.make_satisfied(operator_request)
    await edit_notifies(bot, operator_request)

    await notify_sender(bot, operator_request)


async def edit_notifies(bot: Bot, operator_request: OperatorRequest):
    for el in operator_request.notify_messages_ids:
        chat_id = el.get("chat_id")
        message_id = el.get("message_id")
        await bot.edit_message_reply_markup(
            chat_id,
            message_id,
            reply_markup=get_request_considered_keyboard(),
        )


async def notify_sender(bot: Bot, operator_request: OperatorRequest):
    await bot.send_message(
        operator_request.from_user_id,
        text="Ваше сообщение было рассмотренно",
        reply_to_message_id=operator_request.message_id,
    )
