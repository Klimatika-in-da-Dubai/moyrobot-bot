from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database.dao.shift import CloseShiftDAO, OpenShiftDAO

from app.services.database.dao.shifts_difference import ShiftsDifferenceDAO
from app.services.database.models.shift import CloseShift, OpenShift, Shift
from app.services.database.models.shifts_difference import ShiftsDifference


class ShiftsDifferenceCheck:
    def __init__(self, session: AsyncSession):
        self.closeshiftdao = CloseShiftDAO(session)
        self.openshiftdao = OpenShiftDAO(session)
        self.shiftsdifferencedao = ShiftsDifferenceDAO(session)

    async def check(self, closed_shift: Shift, opened_shift: Shift):
        close_shift: CloseShift = await self.get_close_shift(closed_shift.id)
        open_shift: OpenShift = await self.get_open_shift(opened_shift.id)

        shifts_difference = ShiftsDifference(
            closed_shift_id=closed_shift.id,
            opened_shift_id=opened_shift.id,
            money_difference=open_shift.money_amount - close_shift.money_amount,
        )

        await self.shiftsdifferencedao.add(shifts_difference)

    async def get_open_shift(self, id: int) -> OpenShift:
        open_shift = await self.openshiftdao.get_by_id(id)
        if open_shift is None:
            raise RuntimeError("Open shift can't be None")
        return open_shift

    async def get_close_shift(self, id: int) -> CloseShift:
        close_shift = await self.closeshiftdao.get_by_id(id)
        if close_shift is None:
            raise RuntimeError("Close shift can't be None")
        return close_shift
