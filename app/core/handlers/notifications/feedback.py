from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.keyboards.notifications.feedback import FeedbackNotifyCB
from app.services.database.dao.feedback import FeedbackDAO


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

    await cb.answer()

    await feedbackdao.make_checked(feedback)
    await cb.message.edit_reply_markup()  # type: ignore

    await bot.send_message(
        feedback.from_user_id,
        text="Ваше сообщение было рассмотренно",
        reply_to_message_id=feedback.message_id,
    )
