import pytest
from app.services.database.models.shift import Shift
from test.models.shift.conftest import create_shift


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (create_shift(9), True),
        (create_shift(10), True),
        (create_shift(21), False),
        (create_shift(18), False),
        (create_shift(17), True),
        (create_shift(21, 9), False),
        (create_shift(13), True),
        (create_shift(5), False),
    ],
)
def test_shift_is_daily(test_input: Shift, expected: bool):
    assert test_input.is_daily_shift() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (create_shift(9), False),
        (create_shift(10), False),
        (create_shift(21), True),
        (create_shift(21, 9), True),
        (create_shift(13), False),
        (create_shift(5), True),
    ],
)
def test_shift_is_nightly(test_input: Shift, expected: bool):
    assert test_input.is_nightly_shift() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (create_shift(9), False),
    ],
)
def test_nightly_shift_should_be_closed(test_input, expected):
    assert True
