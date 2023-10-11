from aiogram import Router
from app.core.handlers.admin.cashbox_replenishment.menu import menu_router

cashbox_replenishment_router = Router()
cashbox_replenishment_router.include_routers(menu_router)
