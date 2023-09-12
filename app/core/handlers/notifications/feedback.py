from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.notifications.feedback import FeedbackNotifyCB
from app.services.database.dao.feedback import FeedbackDAO
from app.services.database.models.feedback import Feedback


feedback_router = Router()


@feedback_router.callback_query(FeedbackNotifyCB.filter())
async def cb_feedback_notify_check(
    cb: CallbackQuery,
    bot: Bot,
    callback_data: FeedbackNotifyCB,
    session: async_sessionmaker,
):
    feedbackdao = FeedbackDAO(session)
    feedback = await feedbackdao.get_by_id(id_=callback_data.feedback_id)
    if feedback is None:
        await cb.answer("Произошла ошибка в базе данных", show_alert=True)
        return

    if feedback.checked is True:
        await cb.answer("Сообщение уже было рассмотренно", show_alert=True)
        return

    await cb.answer()

    await feedbackdao.make_checked(feedback)
    await edit_notifies(bot, feedback)
    await notify_sender(bot, feedback)


async def edit_notifies(bot: Bot, feedback: Feedback):
    for el in feedback.notify_messages_ids:
        chat_id = el.get("chat_id")
        message_id = el.get("message_id")
        await bot.edit_message_reply_markup(chat_id, message_id)


async def notify_sender(bot: Bot, feedback: Feedback):
    await bot.send_message(
        feedback.from_user_id,
        text="Ваше сообщение было рассмотренно",
        reply_to_message_id=feedback.message_id,
    )
