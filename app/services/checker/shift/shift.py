from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.checker.shift.cashbox.checker import CashboxChecker
from app.services.database.dao.shift_check import ShiftCheckDAO
from app.services.database.models.shift import Shift
from app.services.database.models.shift_check import ShiftCheck


class ShiftChecker:
    def __init__(self, session: async_sessionmaker):
        self.checkers = [CashboxChecker(session)]
        self.shiftcheckdao = ShiftCheckDAO(session)

    async def check(self, shift: Shift):
        shift_check = ShiftCheck(id=shift.id)
        for checker in self.checkers:
            await checker.check(shift, shift_check)

        await self.shiftcheckdao.add(shift_check)
