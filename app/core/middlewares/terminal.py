from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.parser.terminal_session import TerminalSession


class TerminalSessionMiddleware(BaseMiddleware):
    def __init__(self, terminal_session: TerminalSession, param_name: str = "terminal"):
        super().__init__()
        self.param_name = param_name
        self.session_pool = terminal_session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data[self.param_name] = self.session_pool
        return await handler(event, data)
