from aiogram import Router
from app.core.handlers.menu import menu_router
from app.core.handlers.commands import commands_router
from app.core.handlers.admin import admin_router
from app.core.handlers.operator import operator_router
from app.core.handlers.notifications import notifications_router
from app.core.handlers.operator_request import operator_request_router


handlers_router = Router()

handlers_router.include_routers(
    menu_router,
    admin_router,
    operator_router,
    notifications_router,
    commands_router,
    operator_request_router,
)
