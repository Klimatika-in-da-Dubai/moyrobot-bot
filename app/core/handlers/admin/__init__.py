from aiogram import Router
from app.core.handlers.admin.menu import menu_router
from app.core.handlers.admin.users import user_section_router

admin_router = Router()
admin_router.include_routers(menu_router, user_section_router)
