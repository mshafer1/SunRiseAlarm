import math
from flags import Flags
from datetime import datetime
import json
import uuid
from tinydb_serialization import Serializer


# region testables


class TestableDateTime(object):
    @classmethod
    def today(cls):
        return datetime.today()

    @classmethod
    def now(cls):
        return datetime.now()


class _MockController():
    def __init__(self):
        self.values = {}
        self._range = 255 # pigpio defaults to 255

    @classmethod
    def pi(cls):
        return _MockController()

    def stop(self):
        pass

    def set_PWM_dutycycle(self, pin, value):
        self.values[pin] = value

    def read(self, pin):
        return self.values[pin]
    
    def set_PWM_range(self, pin, range):
        assert 25 <= range <= 4000
        self._range = range




class _MockPWM_LED(object):
    def __init__(self, pin):
        self._value = 0
        self._pin = pin

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, input):
        self._value = input
        return self._value

# endregion


class Days(Flags):
    ALL = 127  # next value would be 128, so 127 is sum of all current (through binary math properties)
    WEEKDAYS = 62 # Sunday = 64, all before = 63, minus Saturday = 62
    SUNDAY = 64
    MONDAY = 32
    TUESDAY = 16
    WEDNESDAY = 8
    THURSDAY = 4
    FRIDAY = 2
    SATURDAY = 1

    @classmethod
    def increment(cls, object):
        day_base_value = int(math.log(int(object), 2))
        next_day_base_value = (day_base_value - 1)%7
        return Days(int(math.pow(2, next_day_base_value)))


class DaysSerializer(Serializer):
    OBJ_CLASS = Days

    @staticmethod
    def encode(obj):
        return str(int(obj))

    @staticmethod
    def decode(s):
        return Days(int(s))


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
    inverted_value = 6 - int(math.log(int(day), 2))
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

