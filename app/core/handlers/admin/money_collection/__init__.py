from aiogram import Router
from app.core.handlers.admin.money_collection.menu import menu_router

money_collection_router = Router()
money_collection_router.include_routers(menu_router)
