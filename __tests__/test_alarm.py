import unittest
from unittest.mock import patch
from datetime import datetime

import pytest

from alarm import Alarm
import utilities
from utilities import Days
import config
import _test_utils


@pytest.fixture()
def default_alarm():
    alarm = Alarm()
    alarm.add_target_day(Days.SUNDAY)
    alarm.target_hour = 6
    alarm.target_minute = 0
    yield alarm


@pytest.mark.parametrize("day", Days)
def test__new_alarm__add_target_day__target_days_matches(day):
    alarm = Alarm()

    alarm.add_target_day(day)

    assert day == alarm.target_days


# using multiple parametrize tests all combinations
@pytest.mark.parametrize("day1", Days)
@pytest.mark.parametrize("day2", Days)
def test__alarm_with_day__add_target_day__target_days_matches_union(day1, day2):
    alarm = Alarm()
    alarm.add_target_day(day1)

    alarm.add_target_day(day2)

    assert all(
        [
            day1 & alarm.target_days,  # day1 flag got set
            day2 & alarm.target_days,  # day2 flag got set
        ]
    )


@pytest.mark.parametrize("days_set", Days)
@pytest.mark.parametrize("day_to_remove", Days)
def test__alarm_with_day_set__remove_target_day__unsets_that_days_flag(days_set, day_to_remove):
    alarm = Alarm()
    alarm.add_target_day(days_set)

    alarm.remove_target_day(day_to_remove)

    assert alarm.target_days & day_to_remove == Days(
        0
    )  # There should be no overlap between still set bits and the day to remove


# NOTE: Jan 1, 2006 is used because it is a sunday - yielding easy translation from day of Jan to day of week.
@pytest.mark.parametrize(
    "mock_datetime, set_days, expected_day",
    (
        (datetime(2006, 1, 1, 0, 0), Days.SUNDAY, Days.SUNDAY),  # midnight, next is today
        (
            datetime(2006, 1, 1, 6, 30),
            Days.SUNDAY,
            Days.SUNDAY,
        ),  # after alarm time, same day next week
        (
            datetime(2006, 1, 1, 6, 30),
            Days.SUNDAY + Days.MONDAY,
            Days.MONDAY,
        ),  # after time, return tomorrow
        (
            datetime(2006, 1, 2, 6, 30),
            Days.SUNDAY + Days.MONDAY,
            Days.SUNDAY,
        ),  # after time on Monday, return next week
    ),
)
def test__mock_date__next_day__returns_expected_day(mock_datetime, set_days, expected_day, freezer):
    freezer.move_to(mock_datetime)
    alarm = Alarm()
    alarm.add_target_day(set_days)
    alarm.target_hour = 6
    alarm.target_minute = 0

    next_day = alarm.next_day

    assert expected_day == next_day


# NOTE: Jan 1, 2006 is used because it is a sunday - yielding easy translation from day of Jan to day of week.
@pytest.mark.parametrize(
    "mock_datetime, set_days, expected_target",
    (
        (datetime(2006, 1, 1, 5, 59), Days.SUNDAY, datetime(2006, 1, 1, 6, 0)),  # one minute away
        (
            datetime(2006, 1, 1, 6, 1),
            Days.SUNDAY,
            datetime(2006, 1, 8, 6, 0),
        ),  # minute after - give me next week
        (
            datetime(2006, 1, 1, 6, 1),
            Days.SUNDAY + Days.MONDAY,
            datetime(2006, 1, 2, 6, 0),
        ),  # minute after - give me tomorrow
        (
            datetime(2006, 1, 3, 5, 0),
            Days.SUNDAY,
            datetime(2006, 1, 8, 6, 0),
        ),  # sever days later - give me next week
    ),
)
def test__mock_date__taget_datetime__returns_expected_value(
    mock_datetime, set_days, expected_target, freezer
):
    freezer.move_to(mock_datetime)
    alarm = Alarm()
    alarm.add_target_day(set_days)
    alarm.target_hour = 6
    alarm.target_minute = 0

    target = alarm.target_datetime

    assert expected_target == target


@pytest.mark.parametrize(
    "current_time, expected_value",
    (
        (datetime(2006, 1, 1, 6, config.after_wakeup_on_time), 100),  # last minute to be on
        (datetime(2006, 1, 1, 6, config.after_wakeup_on_time + 1), 0),  # time to turn off
        (
            datetime(
                2006,
                1,
                1,
                *_test_utils.normalize_hours_minutes(6, -(config.after_wakeup_on_time + 1)),
            ),
            0,
        ),  # 1 minute before time to start turning on
        (datetime(2006, 1, 1, 6, 0), 100),  # fully on at target time
    ),
)
def test__current_time__alarm_get_desired_brightness__returns_expected_value(
    current_time, expected_value, default_alarm, freezer
):
    freezer.move_to(current_time)

    value = default_alarm.get_desired_brightness()

    assert expected_value == value


@pytest.mark.parametrize(
    "current_time, minimum, maximum",
    (
        (
            datetime(
                2006,
                1,
                1,
                *_test_utils.normalize_hours_minutes(6, -(config.after_wakeup_on_time - 1)),
            ),
            0.01,
            10,
        ),  # slightly on one minute into wakeup period
        (
            datetime(2006, 1, 1, *_test_utils.normalize_hours_minutes(6, -1)),
            95,
            100,
        ),  # slightly on one minute into wakeup period
    ),
)
def test__current_time__alarm_get_desired_brightness_returns_result_within_acceptable_margins(
    current_time, minimum, maximum, default_alarm, freezer
):
    freezer.move_to(current_time)

    value = default_alarm.get_desired_brightness()

    assert minimum <= value <= maximum


def test__disabled_alarm__stays_off(default_alarm, freezer):
    freezer.move_to(datetime(2006, 1, 1, 6, 0))
    default_alarm.active = False

    brighness = default_alarm.get_desired_brightness()

    assert brighness == 0


def test__disabled_alarm__stays_off(default_alarm, freezer):
    freezer.move_to(datetime(2006, 1, 1, 6, 0))
    default_alarm.active = False

    brighness = default_alarm.get_desired_brightness()

    assert brighness == 0
