from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.database.dao.consumable_request import ConsumableRequestDAO
from app.services.database.models.consumable_request import (
    Consumable,
    ConsumableRequest,
)
from app.services.database.models.shift import CloseShift, OpenShift


async def check_for_consumables(
    shift: OpenShift | CloseShift, session: async_sessionmaker
):
    needed_consumables = get_needed_consumables(shift)
    if not needed_consumables:
        return

    consumable_request_dao = ConsumableRequestDAO(session)
    for consumable in needed_consumables:
        last_request = await consumable_request_dao.get_last_consumable_request(
            consumable
        )

        if last_request is not None and not last_request.satisfied:
            continue

        consumable_request = ConsumableRequest(consumable=consumable)
        await consumable_request_dao.add_consumable_request(consumable_request)


def get_needed_consumables(shift: OpenShift | CloseShift) -> list[Consumable]:
    needed_consumables = []
    if (
        shift.shampoo_count is None or shift.shampoo_count <= 1
    ):  # or shift.shampoo_check:
        needed_consumables.append(Consumable.SHAMPOO)

    if shift.foam_count is None or shift.foam_count <= 1:  #  or shift.foam_check:
        needed_consumables.append(Consumable.FOAM)

    if shift.wax_count is None or shift.wax_count <= 1:  # or shift.wax_check:
        needed_consumables.append(Consumable.WAX)

    if shift.coins_check:
        needed_consumables.append(Consumable.COINS)

    if shift.napkins_check:
        needed_consumables.append(Consumable.NAPKINS)

    return needed_consumables
