#!/usr/bin/env python3


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
        target = target.replace(hour=self.target_hour, minute=self.target_minute, second=0) # returns new target time

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

