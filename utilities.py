import math
from enum import Flag
from datetime import datetime
import unittest
import json
import uuid

# region testables

class TestableDateTime(object):
    @classmethod
    def today(cls):
        return datetime.today()

    @classmethod
    def now(cls):
        return datetime.now()


class _MockPWM_LED(object):
    def __init__(self, pin):
        self.value = 0
        self._pin = pin

# endregion


# from https://stackoverflow.com/a/6579139/8100990
def object_decoder(obj):
    if '__type__' in obj and obj['__type__'] == 'Days':
        return Days(obj['value'])
    return obj

# from: https://stackoverflow.com/a/48159596/8100990
class SpecialEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        elif isinstance(obj, Days):
            return json.dumps({'__type__': 'Days', 'value': obj.value})
        else:
            return json.JSONEncoder.default(self, obj)


class Days(Flag):
    ALL = 127  # next value would be 128, so 127 is sum of all current (through binary math properties)
    SUNDAY = 64
    MONDAY = 32
    TUESDAY = 16
    WEDNESDAY = 8
    THURSDAY = 4
    FRIDAY = 2
    SATURDAY = 1
    NONE = 0

    @classmethod
    def increment(cls, object):
        day_base_value = int(math.log(object.value, 2))
        next_day_base_value = (day_base_value - 1)%7
        return Days(math.pow(2, next_day_base_value))

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value


# region methods
def convert_datetime_weekday_to_zero_sunday(weekday):
    """
    Python weekday yields values of 0-6 with Mon as 0 and Sun as 6; we want to scale this so Sun is 0 and Sat is 6
    """
    return (weekday + 1) % 7


def convert_weekday_to_days_flag(weekday):
    """

    :param weekday: int Sun = 0, Sat = 6
    :return: Days.{corresponding day}
    """

    inverted_value = 6 - weekday
    return Days(2 ** inverted_value)


def convert_days_flag_to_weekday(day):
    """

    :param day: Days flag
    :return: weekday (Sun = 0, Sat = 6)
    """
    inverted_value = 6 - int(math.log(day.value, 2))
    return inverted_value


def normalize_time(hours, minutes):
    while minutes < 0:
        hours -= 1
        minutes += 60
    while minutes >= 60:
        minutes -= 60
        hours += 1
    return hours, minutes

# endregion

# region unit tests


class _TestConvertDateTimeToZeroBasedWeekday(unittest.TestCase):
    """
    For reference:
    Original:
        Monday - 0
        Tuesday - 1
        Wednesday - 2
        Thursday - 3
        Friday - 4
        Saturday - 5
        Sunday - 6
    Target:
        Sun - 0
        Mon - 1
        Tues - 2
        Wed - 3
        Thur - 4
        Fri - 5
        Sat - 6
    """
    def test_Sunday_is_0(self):
        self.assertEqual(0, convert_datetime_weekday_to_zero_sunday(6))

    def test_Monday_is_1(self):
        self.assertEqual(1, convert_datetime_weekday_to_zero_sunday(0))

    def test_Saturday_is_6(self):
        self.assertEqual(6, convert_datetime_weekday_to_zero_sunday(5))


class _TestDaysIncrementIncrementsAndWraps(unittest.TestCase):
    def test_Sun_increments_to_Mon(self):
        self.assertEqual(Days.MONDAY, Days.increment(Days.SUNDAY))

    def test_Fri_increments_to_Sat(self):
        self.assertEqual(Days.SATURDAY, Days.increment(Days.FRIDAY))

    def test_Sat_increments_to_Sun(self):
        self.assertEqual(Days.SUNDAY, Days.increment(Days.SATURDAY))


class _TestConvertZeroBasedWeekdayToDaysEnum(unittest.TestCase):
    """
    For reference:
        Sun - 0
        Mon - 1
        Tues - 2
        Wed - 3
        Thur - 4
        Fri - 5
        Sat - 6
    """
    def test_Sun(self):
        self.assertEqual(Days.SUNDAY, convert_weekday_to_days_flag(0))

    def test_Mon(self):
        self.assertEqual(Days.MONDAY, convert_weekday_to_days_flag(1))

    def test_Tue(self):
        self.assertEqual(Days.TUESDAY, convert_weekday_to_days_flag(2))

    def test_Wes(self):
        self.assertEqual(Days.WEDNESDAY, convert_weekday_to_days_flag(3))

    def test_Thu(self):
        self.assertEqual(Days.THURSDAY, convert_weekday_to_days_flag(4))

    def test_Fri(self):
        self.assertEqual(Days.FRIDAY, convert_weekday_to_days_flag(5))

    def test_Sat(self):
        self.assertEqual(Days.SATURDAY, convert_weekday_to_days_flag(6))


class _TestConvertDaysFlagToWeekday(unittest.TestCase):
    def test_Sun_0(self):
        self.assertEqual(0, convert_days_flag_to_weekday(Days.SUNDAY))

    def test_Wen_3(self):
        self.assertEqual(3, convert_days_flag_to_weekday(Days.WEDNESDAY))

    def test_Sat_6(self):
        self.assertEqual(6, convert_days_flag_to_weekday(Days.SATURDAY))

# endregion


if __name__ == '__main__':
    unittest.main()