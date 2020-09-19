import unittest

from utilities import *

# region unit tests


class TestConvertDateTimeToZeroBasedWeekday(unittest.TestCase):
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


class TestDaysIncrementIncrementsAndWraps(unittest.TestCase):
    def test_Sun_increments_to_Mon(self):
        self.assertEqual(Days.MONDAY, Days.increment(Days.SUNDAY))

    def test_Fri_increments_to_Sat(self):
        self.assertEqual(Days.SATURDAY, Days.increment(Days.FRIDAY))

    def test_Sat_increments_to_Sun(self):
        self.assertEqual(Days.SUNDAY, Days.increment(Days.SATURDAY))


class TestConvertZeroBasedWeekdayToDaysEnum(unittest.TestCase):
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


class TestConvertDaysFlagToWeekday(unittest.TestCase):
    def test_Sun_0(self):
        self.assertEqual(0, convert_days_flag_to_weekday(Days.SUNDAY))

    def test_Wen_3(self):
        self.assertEqual(3, convert_days_flag_to_weekday(Days.WEDNESDAY))

    def test_Sat_6(self):
        self.assertEqual(6, convert_days_flag_to_weekday(Days.SATURDAY))

    # can it handle multiple days??


# endregion


if __name__ == "__main__":
    unittest.main()
