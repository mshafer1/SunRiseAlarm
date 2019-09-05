from alarm import Alarm
from alarmComposite import AlarmComposite
from utilities import Days

import unittest
from unittest.mock import patch


class TestTargetDaysReturnsOrOfAllDays(unittest.TestCase):
    def test_empty_composite_yieldsNone(self):
        composite = AlarmComposite()
        self.assertEqual(Days(0), composite.target_days)

    def test_single_yields_that(self):
        composite = AlarmComposite()
        alarm = Alarm()
        composite.add_alarm(alarm)
        self.assertEqual(Days(0), composite.target_days)

        alarm.add_target_day(Days.MONDAY)

        self.assertEqual(Days.MONDAY, composite.target_days)

        alarm.remove_target_day(Days.MONDAY)

        self.assertEqual(Days(0), composite.target_days)

        alarm.add_target_day(Days.ALL)

        self.assertEqual(Days.ALL, composite.target_days)

        alarm.remove_target_day(Days.ALL)
        alarm.add_target_day(Days.WEDNESDAY)

        self.assertEqual(Days.WEDNESDAY, composite.target_days)

    def test_double_yields_or(self):
        composite = AlarmComposite()
        alarm1 = Alarm()
        alarm2 = Alarm()
        composite.add_alarms(alarm1, alarm2)

        alarm1.add_target_day(Days.MONDAY | Days.TUESDAY)
        self.assertEqual(Days.MONDAY | Days.TUESDAY, composite.target_days)

        alarm2.add_target_day(Days.MONDAY | Days.FRIDAY)
        self.assertEqual(Days.MONDAY | Days.TUESDAY | Days.FRIDAY, composite.target_days)


class TestTargetHourReturnsNearestHour(unittest.TestCase):
    def test_empty_composite_throws(self):
        composite = AlarmComposite()
        with self.assertRaises(Exception) as context:
            composite.target_hour
        self.assertTrue('Must have at least one alarm' in str(context.exception))

    def test_single_yields_that(self):
        composite = AlarmComposite()
        alarm = Alarm()
        composite.add_alarm(alarm)
        self.assertEqual(0, composite.target_hour)

        alarm.target_hour = 5

        self.assertEqual(5, composite.target_hour)

    def test_double_yields_nearest(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()

            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.ALL)
            alarm1.target_hour = 7

            alarm2.add_target_day(Days.ALL)
            alarm2.target_hour = 8

            self.assertEqual(7, composite.target_hour)

    def test_double_yields_nearest_two(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()

            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.MONDAY)
            alarm1.target_hour = 7

            alarm2.add_target_day(Days.SUNDAY)
            alarm2.target_hour = 8

            self.assertEqual(8, composite.target_hour)


class TestTargetMinuteReturnsNearestHour(unittest.TestCase):
    def test_empty_composite_throws(self):
        composite = AlarmComposite()
        with self.assertRaises(Exception) as context:
            composite.target_minute
        self.assertTrue('Must have at least one alarm' in str(context.exception))

    def test_single_yields_that(self):
        composite = AlarmComposite()
        alarm = Alarm()
        composite.add_alarm(alarm)
        self.assertEqual(0, composite.target_minute)

        alarm.target_minute = 30

        self.assertEqual(30, composite.target_minute)

    def test_double_yields_nearest(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()

            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.ALL)
            alarm1.target_minute = 15

            alarm2.add_target_day(Days.ALL)
            alarm2.target_minute = 30

            self.assertEqual(15, composite.target_minute)

    def test_double_yields_nearest_two(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()

            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.MONDAY)
            alarm1.target_hour = 6
            alarm1.target_minute = 0

            alarm2.add_target_day(Days.SUNDAY)
            alarm2.target_hour = 8
            alarm2.target_minute = 30

            self.assertEqual(30, composite.target_minute)


class TestNexDayReturnsNearestNextDay(unittest.TestCase):
    def test_empty_composite_throws(self):
        composite = AlarmComposite()
        with self.assertRaises(Exception) as context:
            composite.target_minute
        self.assertTrue('Must have at least one alarm' in str(context.exception))

    def test_single_yields_that(self):
        composite = AlarmComposite()
        alarm = Alarm()
        composite.add_alarm(alarm)
        alarm.add_target_day(Days.MONDAY)

        self.assertEqual(Days.MONDAY, composite.next_day)

    def test_double_yields_nearest(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()

            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.FRIDAY)
            alarm2.add_target_day(Days.SATURDAY)

            self.assertEqual(Days.FRIDAY, composite.next_day)

    def test_double_yields_nearest_two(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()

            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.MONDAY)
            alarm1.target_hour = 5
            alarm1.target_minute = 0

            alarm2.add_target_day(Days.SUNDAY)
            alarm2.target_hour = 5
            alarm2.target_minute = 0

            self.assertEqual(Days.MONDAY, composite.next_day)


class TestDesiredBrightnessYieldsGreatest(unittest.TestCase):
    def test_empty_composite_throws(self):
        composite = AlarmComposite()
        self.assertEqual(0, composite.get_desired_brightness())

    def test_single_yields_that(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006

            composite = AlarmComposite()

            alarm = Alarm()
            composite.add_alarm(alarm)
            alarm.add_target_day(Days.SUNDAY)
            alarm.target_hour = 6
            alarm.target_minute = 5

            self.assertEqual(alarm.get_desired_brightness(), composite.get_desired_brightness())

    def test_double_yields_nearest(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()
            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.FRIDAY)
            alarm1.target_hour = 6
            alarm1.target_minute = 0
            alarm2.add_target_day(Days.SUNDAY)
            alarm2.target_hour = 6
            alarm2.target_minute = 20

            self.assertEqual(alarm2.get_desired_brightness(), composite.get_desired_brightness())

    def test_double_yields_nearest_two(self):
        from datetime import datetime
        with patch('utilities.TestableDateTime') as mock_date:
            mock_date.now.return_value = datetime(2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
            composite = AlarmComposite()

            alarm1 = Alarm()
            alarm2 = Alarm()
            composite.add_alarms(alarm1, alarm2)

            alarm1.add_target_day(Days.SUNDAY)
            alarm1.target_hour = 6
            alarm1.target_minute = 15

            alarm2.add_target_day(Days.SUNDAY)
            alarm2.target_hour = 6
            alarm2.target_minute = 30

            self.assertEqual(alarm1.get_desired_brightness(), composite.get_desired_brightness())

if __name__ == '__main__':
    unittest.main()
