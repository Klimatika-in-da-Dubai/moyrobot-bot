from aiogram import Router
from app.core.handlers.operator.menu import menu_router
from app.core.handlers.operator.manual_start import manual_start_router
from app.core.handlers.operator.promocode import promocode_router
from app.core.handlers.operator.bonus import bonus_router
from app.core.handlers.operator.antifreeze import antifreeze_router
from app.core.handlers.operator.shift import shift_router
from app.core.handlers.operator.refund import refund_router
from app.core.handlers.operator.cleaning import cleaning_router

operator_router = Router(name="operator-router")

operator_router.include_routers(
    menu_router,
    manual_start_router,
    promocode_router,
    bonus_router,
    antifreeze_router,
    shift_router,
    refund_router,
    cleaning_router,
)
