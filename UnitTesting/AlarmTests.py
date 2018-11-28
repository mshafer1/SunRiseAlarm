from alarm import Alarm
import utilities
from utilities import Days
import config

import unittest
from unittest.mock import patch
from datetime import datetime


class TestAlarmAddOrRemoveDays(unittest.TestCase):
    def test_setDay(self):
        alarm = Alarm()
        self.assertEqual(Days(0), alarm.target_days)

        for day in Days:
            alarm.add_target_day(day)
            if day is Days(0):
                self.assertEqual(Days(0), alarm.target_days)
            else:
                self.assertNotEqual(Days(0), alarm.target_days)
            self.assertEqual(day, alarm.target_days)

            # reset
            alarm.target_days = Days(0)

    def test_addDay(self):
        alarm = Alarm()
        self.assertEqual(Days(0), alarm.target_days)

        for day in Days:
            alarm.add_target_day(day)

            self.assertEqual(day, alarm.target_days & day)  # check it got set
            if day is not Days(0):
                self.assertNotEqual(Days(0), alarm.target_days)

    def test_removeDay(self):
        alarm = Alarm()
        alarm.add_target_day(Days.ALL)
        self.assertEqual(Days.ALL, alarm.target_days)

        for day in Days:
            if day is Days(0):
                alarm.remove_target_day(day)
                self.assertEqual(Days.ALL, alarm.target_days)  # assert removing days that aren't there is a noop
            else:
                alarm.remove_target_day(day)
                self.assertEqual(Days(0), alarm.target_days & day)  # assert that day flag is not set anymore

            # reset it
            alarm.add_target_day(Days.ALL)


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