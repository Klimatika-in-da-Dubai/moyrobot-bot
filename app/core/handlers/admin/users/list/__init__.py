from aiogram import Router
from app.core.handlers.admin.users.list.menu import menu_router
from app.core.handlers.admin.users.list.selected_user import selected_user_router
from app.core.handlers.admin.users.list.change import change_user_router

list_router = Router()
list_router.include_routers(menu_router, selected_user_router, change_user_router)
