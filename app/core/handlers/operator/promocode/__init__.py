from aiogram import Router
from app.core.handlers.operator.promocode.menu import menu_router
from app.core.handlers.operator.promocode.wash_mode import wash_mode_router

promocode_router = Router()

promocode_router.include_routers(menu_router, wash_mode_router)
