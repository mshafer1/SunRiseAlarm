#!/usr/bin/env python3
from unittest.mock import patch

import config


import unittest

from LEDController import *
import utilities
from utilities import Days
from datetime import datetime, timedelta, time


class Alarm(object):
    def __init__(self, PWM_LED):
        self._value = 0
        self._led = PWM_LED
        self.target_days = utilities.Days.NONE
        self.target_hour = 0
        self.target_minute = 0

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
        if self.target_days == utilities.Days.NONE:
            raise Exception("No time set")

        # get current date time
        now = utilities.TestableDateTime.now()

        today = utilities.convert_datetime_weekday_to_zero_sunday(now.weekday())

        today_as_days_flag = utilities.convert_weekday_to_days_flag(today)

        # evaluate next target day (if today is a target day, include if not past alarm time)
        if self.target_days & today_as_days_flag is not utilities.Days.NONE:
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

    def set_brightness(self, percent):
        if percent < 0 or percent > 100:
            raise Exception('Value must be between 0 and 100 (inclusively)')
        self._value = percent
        self._led.value = Alarm._scale(self._value)

    def set(self):
        self.set_brightness(self.get_desired_brightness())

    def get_desired_brightness(self):
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
        elif time_delta.seconds <= desired_time:
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
    def value(self):
        return self._led.value

    @property
    def alarm_passed_today(self):
        # TODO: include if today is an active day
        this_time = utilities.TestableDateTime.now().time()
        return this_time > time(self.target_hour, self.target_minute)

    @classmethod
    def _scale(cls, percent):
        # this is a scaling based on desired percentage to 8 bit power for linear brightness
        eight_bit_val = (.0127 * percent ** 2 + 1.3027 * percent ) // 1.0089

        # scale to [0,1]
        return eight_bit_val / 255


class _MockPWM_LED(object):
    def __init__(self):
        self.value = 0

class _TestAlarmAddOrRemoveDays(unittest.TestCase):
    def test_setDay(self):
        alarm = Alarm(_MockPWM_LED())
        self.assertEqual(Days.NONE, alarm.target_days)

        for day in Days:
            alarm.add_target_day(day)
            if day is Days.NONE:
                self.assertEqual(Days.NONE, alarm.target_days)
            else:
                self.assertNotEqual(Days.NONE, alarm.target_days)
            self.assertEqual(day, alarm.target_days)

            # reset
            alarm.target_days = Days.NONE

    def test_addDay(self):
        alarm = Alarm(_MockPWM_LED())
        self.assertEqual(Days.NONE, alarm.target_days)

        for day in Days:
            alarm.add_target_day(day)

            self.assertEqual(day, alarm.target_days & day)  # check it got set
            if day is not Days.NONE:
                self.assertNotEqual(Days.NONE, alarm.target_days)

    def test_removeDay(self):
        alarm = Alarm(_MockPWM_LED())
        alarm.add_target_day(Days.ALL)
        self.assertEqual(Days.ALL, alarm.target_days)

        for day in Days:
            if day is Days.NONE:
                alarm.remove_target_day(day)
                self.assertEqual(Days.ALL, alarm.target_days)  # assert removing days that aren't there is a noop
            else:
                alarm.remove_target_day(day)
                self.assertEqual(Days.NONE, alarm.target_days & day)  # assert that day flag is not set anymore

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

            alarm = Alarm(_MockPWM_LED())
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(Days.SUNDAY, alarm.next_day)

    def test_NextDate_ReturnsTomorrowWhenTimeHasPassed(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 30)  # 6:30, Sunday, Jan 1st, 2006

            alarm = Alarm(_MockPWM_LED())
            alarm.add_target_day(Days.SUNDAY)
            alarm.add_target_day(Days.MONDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(Days.MONDAY, alarm.next_day)

    def test_NextDate_ReturnsDayNextWeekWhenTimeHasPassed(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 2, 6, 30)  # 6:30, Monday, Jan 2nd, 2006

            alarm = Alarm(_MockPWM_LED())
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
            alarm = Alarm(_MockPWM_LED())
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
            alarm = Alarm(_MockPWM_LED())
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
            alarm = Alarm(_MockPWM_LED())
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
            alarm = Alarm(_MockPWM_LED())
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
            alarm = Alarm(_MockPWM_LED())
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = config.wakeup_time + 1

            self.assertEqual(0, alarm.get_desired_brightness())

    def test_slightly_on_desired_time_minus_one_minutes_early(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm(_MockPWM_LED())
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
            alarm = Alarm(_MockPWM_LED())
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
            alarm = Alarm(_MockPWM_LED())
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(100, alarm.get_desired_brightness())

    def test_fully_on_for_almost_desired_time_after_target(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            hours, minutes = utilities.normalize_time(6, config.after_wakeup_on_time - 1)
            mock_date.now.return_value = datetime(2006, 1, 1, hours, minutes)  # ?, Sunday, Jan 1st, 2006
            alarm = Alarm(_MockPWM_LED())
            alarm.add_target_day(Days.SUNDAY)

            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(100, alarm.get_desired_brightness())

    def test_fully_on_for_desired_time_after_target(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            hours, minutes = utilities.normalize_time(6, config.after_wakeup_on_time)
            mock_date.now.return_value = datetime(2006, 1, 1, hours, minutes)  # ?, Sunday, Jan 1st, 2006
            alarm = Alarm(_MockPWM_LED())
            alarm.add_target_day(Days.SUNDAY)

            alarm.target_hour = 6
            alarm.target_minute = 0

            self.assertEqual(100, alarm.get_desired_brightness())

class _TestAlarmSetConfiguresLED(unittest.TestCase):
    def test_Alarm_Set_LED_On_Full(self):
        led = _MockPWM_LED()
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm(led)
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 0

            alarm.set()
            self.assertEqual(1, led.value)

    def test_Alarm_set_LED_off(self):
        from datetime import datetime
        led = _MockPWM_LED()
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            alarm = Alarm(led)
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = config.wakeup_time + 1

            self.assertEqual(0, led.value)


if __name__ == '__main__':
    unittest.main()
