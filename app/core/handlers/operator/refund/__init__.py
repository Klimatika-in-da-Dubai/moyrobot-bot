from aiogram import Router
from app.core.handlers.operator.refund.menu import menu_router

refund_router = Router()

refund_router.include_routers(menu_router)
