from aiogram import Router
from app.core.handlers.operator.manual_start.menu import manual_start_menu_router


manual_start_router = Router()

manual_start_router.include_router(manual_start_menu_router)
