from aiogram import Router
from app.core.handlers.operator.manual_start_section.menu import (
    manual_start_menu_router,
)
from app.core.handlers.operator.manual_start_section.manual_start_type import (
    manual_start_type_router,
)

from app.core.handlers.operator.manual_start_section.test_manual_start import (
    test_manual_start_router,
)

from app.core.handlers.operator.manual_start_section.service_manual_start import (
    service_manual_start_router,
)
from app.core.handlers.operator.manual_start_section.rewash_manual_start import (
    rewash_manual_start_router,
)

from app.core.handlers.operator.manual_start_section.paid_manual_start import (
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
