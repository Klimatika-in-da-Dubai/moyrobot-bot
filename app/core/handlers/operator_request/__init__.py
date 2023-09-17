from aiogram import Router
from app.core.handlers.operator_request.menu import operator_request_menu_router

operator_request_router = Router()


operator_request_router.include_routers(operator_request_menu_router)
