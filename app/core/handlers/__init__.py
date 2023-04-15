from aiogram import Router
from app.core.handlers.menu import menu_router
from app.core.handlers.admin import admin_router
from app.core.handlers.operator import operator_router

handlers_router = Router()

handlers_router.include_routers(menu_router, admin_router, operator_router)
