from typing import Any, List, Optional, Protocol, Union
from aiogram.methods import EditMessageText, SendMessage

from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


class EditMessageFunc(Protocol):
    def __call__(
        fakeself,
        text: str,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = None,
        entities: Optional[List[MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        **kwargs: Any,
    ) -> EditMessageText:
        ...


class SendMessageFunc(Protocol):
    def __call__(
        fakeself,
        text: str,
        parse_mode: Optional[str] = None,
        entities: Optional[List[MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[
            Union[
                InlineKeyboardMarkup,
                ReplyKeyboardMarkup,
                ReplyKeyboardRemove,
                ForceReply,
            ]
        ] = None,
        **kwargs: Any,
    ) -> SendMessage:
        ...
