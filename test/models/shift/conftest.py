import datetime
import pytest
from typing import Optional
from app.services.database.models.shift import Shift


def create_shift(open_hour: int, close_hour: Optional[int] = None) -> Shift:
    open_date = datetime.datetime(year=2023, month=1, day=1, hour=open_hour)
    shift = Shift(id=0, open_date=open_date)
    if not close_hour:
        return shift

    if open_hour <= close_hour:
        close_date = datetime.datetime(year=2023, month=1, day=1, hour=close_hour)
    else:
        close_date = datetime.datetime(year=2023, month=1, day=2, hour=close_hour)
    shift.close_date = close_date
    return shift


@pytest.fixture
def freeze(monkeypatch):
    """Now() manager patches datetime return a fixed, settable, value
    (freezes time)
    """
    import datetime

    original = datetime.datetime

    class FreezeMeta(type):
        def __instancecheck__(self, instance):
            if type(instance) == original or type(instance) == Freeze:
                return True

    class Freeze(datetime.datetime):
        __metaclass__ = FreezeMeta

        @classmethod
        def freeze(cls, val):
            cls.frozen = val

        @classmethod
        def now(cls):
            return cls.frozen

        @classmethod
        def delta(cls, timedelta=None, **kwargs):
            """Moves time fwd/bwd by the delta"""
            from datetime import timedelta as td

            if not timedelta:
                timedelta = td(**kwargs)
            cls.frozen += timedelta

    monkeypatch.setattr(datetime, "datetime", Freeze)
    Freeze.freeze(original.now())
    return Freeze
