from aiogram import Router
from app.core.handlers.feedback.menu import feedback_menu_router

feedback_router = Router()


feedback_router.include_routers(feedback_menu_router)
