from aiogram import Router
from app.core.handlers.admin.menu import menu_router
from app.core.handlers.admin.users import user_section_router
from app.core.handlers.admin.money_collection import money_collection_router
from app.core.handlers.admin.cashbox_replenishment import cashbox_replenishment_router
from app.core.handlers.admin.groups import groups_router

admin_router = Router()
admin_router.include_routers(
    menu_router,
    user_section_router,
    money_collection_router,
    cashbox_replenishment_router,
    groups_router,
)
