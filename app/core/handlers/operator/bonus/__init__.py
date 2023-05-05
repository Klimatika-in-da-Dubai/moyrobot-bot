from aiogram import Router
from app.core.handlers.operator.bonus.menu import menu_router

bonus_router = Router()

bonus_router.include_routers(menu_router)
