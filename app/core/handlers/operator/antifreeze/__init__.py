from aiogram import Router
from app.core.handlers.operator.antifreeze.menu import menu_router


antifreeze_router = Router()

antifreeze_router.include_routers(menu_router)
