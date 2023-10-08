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
        close_shift: CloseShift = await self.closeshiftdao.get_by_id(  # type: ignore
            closed_shift.id
        )
        open_shift: OpenShift = await self.openshiftdao.get_by_id(  # type:ignore
            opened_shift.id
        )

        shifts_difference = ShiftsDifference(
            closed_shift_id=closed_shift.id,
            opened_shift_id=opened_shift.id,
            money_difference=open_shift.money_amount - close_shift.money_amount,
        )

        await self.shiftsdifferencedao.add(shifts_difference)
