from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.base import Action
from app.services.database.models.feedback import Feedback


class FeedbackNotifyCB(CallbackData, prefix="feedback_not"):
    action: Action
    feedback_id: int


def get_feedback_keyboard(feedback: Feedback):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Сделано",
            callback_data=FeedbackNotifyCB(
                action=Action.SELECT, feedback_id=feedback.id
            ).pack(),
        )
    )
    return builder.as_markup()
