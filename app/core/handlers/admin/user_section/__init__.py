from aiogram import Router
from app.core.handlers.admin.user_section.menu import menu_router
from app.core.handlers.admin.user_section.add_user import add_user_router

user_section_router = Router()

user_section_router.include_routers(menu_router, add_user_router)
