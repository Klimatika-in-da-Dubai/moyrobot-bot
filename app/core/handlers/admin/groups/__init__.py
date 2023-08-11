from aiogram import Router
from app.core.handlers.admin.groups.menu import menu_router
from app.core.handlers.admin.groups.select import select_router
from app.core.handlers.admin.groups.mailing import mailing_router

groups_router = Router()

groups_router.include_routers(menu_router, select_router, mailing_router)
