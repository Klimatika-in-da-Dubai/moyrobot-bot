from aiogram import Router

from app.core.handlers.operator.cleaning.menu import menu_router
from app.core.handlers.operator.cleaning.place import place_router
from app.core.handlers.operator.cleaning.work import work_router

cleaning_router = Router()

cleaning_router.include_routers(menu_router, place_router, work_router)
