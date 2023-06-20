from aiogram import Router
from app.core.handlers.admin.users.menu import menu_router
from app.core.handlers.admin.users.add import add_router
from app.core.handlers.admin.users.list import list_router

user_section_router = Router()

user_section_router.include_routers(menu_router, add_router, list_router)
