import unittest
from unittest.mock import patch
from datetime import datetime

import pytest

from alarm import Alarm
import utilities
from utilities import Days
import config



@pytest.mark.parametrize("day", Days)
def test__new_alarm__add_target_day__target_days_matches(day):
    alarm = Alarm()

    alarm.add_target_day(day)

    assert day == alarm.target_days


# using multiple parametrize tests all combinations
@pytest.mark.parametrize("day1", Days)
@pytest.mark.parametrize("day2", Days)
def test__alarm_with_day__add_target_day__target_days_matches_union(day1,day2):
    alarm = Alarm()
    alarm.add_target_day(day1)

    alarm.add_target_day(day2)

    assert all([
        day1 & alarm.target_days, # day1 flag got set
        day2 & alarm.target_days, # day2 flag got set
    ]) 

@pytest.mark.parametrize("days_set", Days)
@pytest.mark.parametrize("day_to_remove", Days)
def test__alarm_with_day_set__remove_target_day__unsets_that_days_flag(days_set, day_to_remove):
    alarm = Alarm()
    alarm.add_target_day(days_set)

    alarm.remove_target_day(day_to_remove)

    assert alarm.target_days & day_to_remove == Days(0) # There should be no overlap between still set bits and the day to remove


class TestAlarmGetNextDay(unittest.TestCase):
    def testTestDateTime_YieldsActualDateTime(self):
        from datetime import datetime
        today = datetime.today()
        testable_today = utilities.TestableDateTime.today()
        self.assertEqual(today, testable_today)

        now = datetime.now()
        testable_now = utilities.TestableDateTime.now()
        self.assertEqual(now.hour, testable_now.hour)
        self.assertEqual(now.minute, testable_now.minute)

    def test_NextDate_ReturnsTodayWhenTimeHasNotPassedYet(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 0, 0)  # midnight, Sunday, Jan 1st, 2006

            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(Days.SUNDAY, alarm.next_day)

    def test_NextDate_ReturnsTomorrowWhenTimeHasPassed(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 30)  # 6:30, Sunday, Jan 1st, 2006

            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.add_target_day(Days.MONDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(Days.MONDAY, alarm.next_day)

    def test_NextDate_ReturnsDayNextWeekWhenTimeHasPassed(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 2, 6, 30)  # 6:30, Monday, Jan 2nd, 2006

            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.add_target_day(Days.MONDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(Days.SUNDAY, alarm.next_day)


class TestAlarmGetTargetDateTime(unittest.TestCase):
    def test_today_times(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 5, 29)  # 5:29, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(alarm.next_day, Days.SUNDAY)
            target = alarm.target_datetime

            self.assertEqual(target.hour, alarm.target_hour)
            self.assertEqual(target.minute, alarm.target_minute)
            now = utilities.TestableDateTime.now()
            self.assertEqual(target.day, now.day)

    def test_today_passed_times(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 1)  # 6:01, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            target = alarm.target_datetime
            self.assertEqual(target.hour, alarm.target_hour)
            self.assertEqual(target.minute, alarm.target_minute)
            now = utilities.TestableDateTime.now()
            self.assertEqual(target.day, now.day + 7)  # a week from now

    def test_tomorrow_times(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 1)  # 6:01, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.MONDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            target = alarm.target_datetime
            self.assertEqual(target.hour, alarm.target_hour)
            self.assertEqual(target.minute, alarm.target_minute)
            now = utilities.TestableDateTime.now()
            self.assertEqual(target.day, now.day + 1) # tomorrow

    def test_next_week_times(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 3, 0, 0)  # midnight, Tuesday, Jan 3rd, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            target = alarm.target_datetime
            self.assertEqual(target.hour, alarm.target_hour)
            self.assertEqual(target.minute, alarm.target_minute)
            self.assertEqual(target.day, 8)  # Sunday the 8th


class TestGradualFadeUpOnTime(unittest.TestCase):
    def test_off_desired_time_plus_one_minutes_early(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = config.wakeup_time + 1

            self.assertEqual(0, alarm.get_desired_brightness())

    def test_slightly_on_desired_time_minus_one_minutes_early(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = config.wakeup_time - 1

            # assert desired brightness is a smal value [.01,10]
            self.assertLessEqual(.01, alarm.get_desired_brightness())
            self.assertLessEqual(alarm.get_desired_brightness(), 10)

    def test_nearly_completly_on_target_time_minus_one_minute(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)

            hour, minute = utilities.normalize_time(6, 1)

            alarm.target_hour = hour
            alarm.target_minute = minute

            # assert desired brightness is a large value [95,100]
            self.assertLessEqual(95, alarm.get_desired_brightness())
            self.assertLessEqual(alarm.get_desired_brightness(), 100)

    def test_fully_on_at_target_time(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(100, alarm.get_desired_brightness())

    def test_fully_on_for_almost_desired_time_after_target(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            hours, minutes = utilities.normalize_time(6, config.after_wakeup_on_time - 1)
            mock_date.now.return_value = datetime(2006, 1, 1, hours, minutes)  # ?, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)

            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(100, alarm.get_desired_brightness())

    def test_fully_on_for_desired_time_after_target(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            hours, minutes = utilities.normalize_time(6, config.after_wakeup_on_time)
            mock_date.now.return_value = datetime(2006, 1, 1, hours, minutes)  # ?, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)

            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(100, alarm.get_desired_brightness())

    def test_fully_off_on_other_days_than_target(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            hours, minutes = utilities.normalize_time(6, config.after_wakeup_on_time)
            mock_date.now.return_value = datetime(2006, 1, 1, hours, minutes)  # ?, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.FRIDAY)

            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(0, alarm.get_desired_brightness())

    def test_fully_off_on_days_after_target(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 6th, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.FRIDAY)

            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(0, alarm.get_desired_brightness())


class TestAlarmDisabledStaysOff(unittest.TestCase):
    def test_AlarmThatIsDisabledStaysAtValueZero(self):
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm()
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0
            alarm.active = False

            self.assertEqual(0, alarm.get_desired_brightness())

            alarm.active = True
            self.assertEqual(100, alarm.get_desired_brightness())


if __name__ == '__main__':
    unittest.main()