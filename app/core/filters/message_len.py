from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Filter


class MessageLenght(Filter):
    def __init__(self, min_length: int = 1, max_length: int = 100):
        self.min_length = min_length
        self.max_length = max_length

    async def __call__(self, message: types.Message) -> bool:
        if len(message.md_text) < self.min_length:
            await message.answer(
                f"Ваше сообщение слишком длинное (минимум {self.min_length} символов).",
                parse_mode=ParseMode.HTML,
            )
            return False

        if len(message.md_text) > self.max_length:
            await message.answer(
                f"Ваше сообщение слишком длинное (максимум {self.max_length} символов)."
                "Если вы используете форматирование, то уберите его или сделайте текст меньше",
                parse_mode=ParseMode.HTML,
            )
            return False

        return True
