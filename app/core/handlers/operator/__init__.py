from aiogram import Router
from app.core.handlers.operator.menu import menu_router
from app.core.handlers.operator.manual_start_section import manual_start_router
from app.core.handlers.operator.promocode import promocode_router
from app.core.handlers.operator.bonus import bonus_router

operator_router = Router(name="operator-router")

operator_router.include_routers(
    menu_router, manual_start_router, promocode_router, bonus_router
)
