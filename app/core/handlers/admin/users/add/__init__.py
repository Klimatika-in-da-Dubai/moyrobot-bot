from aiogram import Router
from app.core.handlers.admin.users.add.add import add_user_router
from app.core.handlers.admin.users.add.mailing import mailing_router

add_router = Router()

add_router.include_routers(add_user_router, mailing_router)
