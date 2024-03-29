from aiogram import Router
from app.core.handlers.notifications.payment_check import card_payment_router
from app.core.handlers.notifications.bonus import bonus_router
from app.core.handlers.notifications.promocode import promocode_router
from app.core.handlers.notifications.operator_request import operator_request_router
from app.core.handlers.notifications.consumable_request import consumable_request_router

notifications_router = Router()

notifications_router.include_routers(
    card_payment_router,
    bonus_router,
    promocode_router,
    operator_request_router,
    consumable_request_router,
)
