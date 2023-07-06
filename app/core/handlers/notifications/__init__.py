from aiogram import Router
from app.core.handlers.notifications.payment_check import card_payment_router

notifications_router = Router()

notifications_router.include_routers(card_payment_router)
