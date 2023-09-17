from aiogram import Router
from app.core.handlers.operator.shift.menu import menu_router
from app.core.handlers.operator.shift.robot import robot_check_router
from app.core.handlers.operator.shift.open import open_shift_router
from app.core.handlers.operator.shift.close import close_shift_router
from app.core.handlers.operator.shift.operator import operator_name_router
from app.core.handlers.operator.shift.chemistry import chemistry_router


shift_router = Router()

shift_router.include_routers(
    menu_router,
    open_shift_router,
    close_shift_router,
    robot_check_router,
    operator_name_router,
    chemistry_router,
)
