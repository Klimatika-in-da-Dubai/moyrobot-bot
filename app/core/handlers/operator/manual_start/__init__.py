from aiogram import Router
from app.core.handlers.operator.manual_start.menu import (
    manual_start_menu_router,
)
from app.core.handlers.operator.manual_start.type import (
    manual_start_type_router,
)

from app.core.handlers.operator.manual_start.test import (
    test_manual_start_router,
)

from app.core.handlers.operator.manual_start.service import (
    service_manual_start_router,
)
from app.core.handlers.operator.manual_start.rewash import (
    rewash_manual_start_router,
)

from app.core.handlers.operator.manual_start.paid import (
    paid_manual_start_router,
)

manual_start_router = Router()

manual_start_router.include_routers(
    manual_start_menu_router,
    manual_start_type_router,
    test_manual_start_router,
    service_manual_start_router,
    rewash_manual_start_router,
    paid_manual_start_router,
)
