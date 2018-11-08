#!/usr/bin/env python3
from unittest.mock import patch

import config


import unittest

from LEDController import *
import utilities
from utilities import Days
from datetime import datetime, timedelta, time


class Alarm(object):
    def __init__(self, **kwargs):
        self._value = 0
        self.target_days = utilities.Days(0)
        self.target_hour = 0
        self.target_minute = 0
        self.active = True
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

    def add_target_day(self, day):
        self.target_days |= day

    def remove_target_day(self, day):
        other_days = Days.ALL & ~(day)
        self.target_days &= other_days # set to days that are set and in other_days

    def set_time(self, hour, minute):
        """
        Set the target time to reach full brightness
        :param hour: int [0-23] in local time zone
        :param minute: int [0-59] in local time zone
        :return: None
        """
        if hour < 0 or hour > 23:
            raise Exception('Hour must be between 0 and 23 (inclusively)')
        if minute < 0 or minute > 59:
            raise Exception('Minutes must be between 0 and 59 (inclusively)')
        self.target_hour = hour
        self.target_minute = minute


    @property
    def next_day(self):
        """
        Get the next target day as a Day enum
        :return: Day enum
        """
        if self.target_days == utilities.Days(0):
            raise Exception("No time set")

        # get current date time
        now = utilities.TestableDateTime.now()

        today = utilities.convert_datetime_weekday_to_zero_sunday(now.weekday())

        today_as_days_flag = utilities.convert_weekday_to_days_flag(today)

        # evaluate next target day (if today is a target day, include if not past alarm time)
        if today_as_days_flag in self.target_days:
            if now.hour < self.target_hour or now.hour == self.target_hour and now.minute <= self.target_minute:
                return today_as_days_flag

        target_day = original = today_as_days_flag
        target_day = Days.increment(target_day)
        while target_day != original:
            if self.target_days & target_day == target_day:
                return target_day
            target_day = Days.increment(target_day)
        if self.target_days & target_day == target_day:  # if we wrapped, check one more time
            return target_day
        raise Exception("Could not find next target day.")

    def get_desired_brightness(self):
        """

        :return: desired brightness [0,100]
        """
        if not self.active:
            return 0

        time = utilities.TestableDateTime.now()
        time_delta = self.target_datetime - time

        if self.alarm_passed_today:
            desired_after_on_time = config.after_wakeup_on_time * 60
            # check if we should still be on
            today_target_time = datetime(time.year, time.month, time.day, self.target_hour, self.target_minute)
            time_delta = today_target_time - time + timedelta(minutes=config.after_wakeup_on_time)

            if time_delta.seconds < desired_after_on_time:
                return 100

        # else figure out how bright for today
        desired_time = config.wakeup_time * 60  # convert to seconds
        if time_delta.seconds > desired_time:
            return 0
        elif time_delta.total_seconds() <= desired_time:
            percent = (100 * time_delta.seconds) / desired_time
            return 100 - percent
        else:
            return 0

    @property
    def target_datetime(self):
        time = utilities.TestableDateTime.now()
        next_day = self.next_day
        this_day = utilities.convert_datetime_weekday_to_zero_sunday(time.weekday())

        target = time
        days_delta = utilities.convert_days_flag_to_weekday(next_day) - this_day
        if days_delta == 0:
            # this means the alarm is set weekly, and it is that day, bump it a week if it has passed today
            days_delta += 7 if self.alarm_passed_today else 0
        elif days_delta < 0:
            days_delta += 7 # the day of the week has passed, delta should be positive to the next occurrence

        target += timedelta(days=days_delta)
        target = target.replace(hour=self.target_hour, minute=self.target_minute) # returns new target time

        return target

    @property
    def alarm_passed_today(self):
        today = utilities.TestableDateTime.now().weekday()
        today = utilities.convert_datetime_weekday_to_zero_sunday(today)
        today = utilities.convert_weekday_to_days_flag(today)

        if today & self.target_days != Days(0):
            this_time = utilities.TestableDateTime.now().time()
            return this_time > time(self.target_hour, self.target_minute)
        return False


class _TestAlarmAddOrRemoveDays(unittest.TestCase):
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


class _TestAlarmGetNextDay(unittest.TestCase):
    def test_TestDateTime_YieldsActualDateTime(self):
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


class _TestAlarmGetTargetDateTime(unittest.TestCase):
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


class _TestGradualFadeUpOnTime(unittest.TestCase):
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


class _TestAlarmDisabledStaysOff(unittest.TestCase):
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
