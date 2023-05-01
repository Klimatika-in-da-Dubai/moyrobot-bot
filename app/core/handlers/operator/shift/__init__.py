from aiogram import Router
from app.core.handlers.operator.shift.menu import menu_router
from app.core.handlers.operator.shift.robot import robot_check_router


shift_router = Router()

shift_router.include_routers(menu_router, robot_check_router)
