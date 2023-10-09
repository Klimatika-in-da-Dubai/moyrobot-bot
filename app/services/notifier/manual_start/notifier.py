from typing import Sequence, assert_never

from app.services.database.dao.manual_start import ManualStartDAO
from app.services.database.models.mailing import MailingType
from app.services.database.models.manual_start import (
    ManualStart,
    ManualStartType,
)
from app.services.notifier.base import Notifier
from app.services.notifier.manual_start.senders.corporate import (
    CorporateManualStartSender,
)
from app.services.notifier.manual_start.senders.paid import PaidManualStartSender
from app.services.notifier.manual_start.senders.rewash import RewashManualStartSender
from app.services.notifier.manual_start.senders.serivce import ServiceManualStartSender
from app.services.notifier.manual_start.senders.test import TestManualStartSender


class ManualStartNotifier(Notifier):
    def __init__(self, bot, session):
        super().__init__(
            bot, session, MailingType.MANUAL_START, ManualStartDAO(session)
        )
        self._dao: ManualStartDAO
        self.test_sender = TestManualStartSender(bot, session)
        self.service_sender = ServiceManualStartSender(bot, session)
        self.rewash_sender = RewashManualStartSender(bot, session)
        self.paid_sender = PaidManualStartSender(bot, session)
        self.corporate_sender = CorporateManualStartSender(bot, session)

    async def get_objects_to_notify(self) -> Sequence[ManualStart]:
        return await self._dao.get_unnotified()

    async def make_notified(self, manual_start: ManualStart):
        await self._dao.make_notified(manual_start)

    async def send_notify(self, id: int, manual_start: ManualStart):
        match manual_start.type:
            case ManualStartType.TEST:
                await self.test_sender.send_notify(id, manual_start)
            case ManualStartType.SERVICE:
                await self.service_sender.send_notify(id, manual_start)
            case ManualStartType.REWASH:
                await self.rewash_sender.send_notify(id, manual_start)
            case ManualStartType.PAID:
                await self.paid_sender.send_notify(id, manual_start)
            case ManualStartType.CORPORATE:
                await self.corporate_sender.send_notify(id, manual_start)
            case _ as never:
                assert_never(never)
