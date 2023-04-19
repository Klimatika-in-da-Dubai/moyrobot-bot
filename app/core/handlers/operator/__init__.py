from aiogram import Router
from app.core.handlers.operator.menu import operator_menu_router
from app.core.handlers.operator.manual_start_section import manual_start_router

operator_router = Router(name="operator-router")

operator_router.include_routers(operator_menu_router, manual_start_router)
