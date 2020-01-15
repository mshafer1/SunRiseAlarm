import pytest

from ..alarm import Alarm
from ..alarmComposite import AlarmComposite
from ..utilities import Days
from .. import utilities as utilities

import unittest
from unittest.mock import patch


def get_mock_date():
    name = __name__
    return patch('utilities.TestableDateTime')


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
        self.assertEqual(Days.MONDAY | Days.TUESDAY |
                         Days.FRIDAY, composite.target_days)


# Region Target Hour returns nearest hour
def test_empty_composite_throws():
    composite = AlarmComposite()
    with pytest.raises(Exception) as exc_info:
        composite.target_hour
    assert 'Must have at least one alarm' in exc_info.value.args[0]


def test_single_yields_that():
    composite = AlarmComposite()
    alarm = Alarm()
    composite.add_alarm(alarm)
    assert composite.target_hour == 0

    alarm.target_hour = 5

    assert composite.target_hour == 5


def test_double_yields_nearest(mock_date):
    from datetime import datetime

    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
    composite = AlarmComposite()

    alarm1 = Alarm()
    alarm2 = Alarm()
    composite.add_alarms(alarm1, alarm2)

    alarm1.add_target_day(Days.ALL)
    alarm1.target_hour = 7

    alarm2.add_target_day(Days.ALL)
    alarm2.target_hour = 8

    composite.target_hour == 7


def test_double_yields_nearest_two(mock_date):
    from datetime import datetime
    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
    composite = AlarmComposite()

    alarm1 = Alarm()
    alarm2 = Alarm()
    composite.add_alarms(alarm1, alarm2)

    alarm1.add_target_day(Days.MONDAY)
    alarm1.target_hour = 7

    alarm2.add_target_day(Days.SUNDAY)
    alarm2.target_hour = 8

    assert composite.target_hour == 8
# End Region

# Region Target minute returns nearest hour


def test_empty_composite_throws_on_target_minute():
    composite = AlarmComposite()
    with pytest.raises(Exception) as exc_info:
        composite.target_minute
    assert 'Must have at least one alarm' in exc_info.value.args[0]


def test_single_yields_that_minute():
    composite = AlarmComposite()
    alarm = Alarm()
    composite.add_alarm(alarm)
    assert composite.target_minute == 0

    alarm.target_minute = 30

    assert composite.target_minute == 30


def test_double_yields_nearest_minute(mock_date):
    from datetime import datetime
    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
    composite = AlarmComposite()

    alarm1 = Alarm()
    alarm2 = Alarm()
    composite.add_alarms(alarm1, alarm2)

    alarm1.add_target_day(Days.ALL)
    alarm1.target_minute = 15

    alarm2.add_target_day(Days.ALL)
    alarm2.target_minute = 30

    assert composite.target_minute == 15


def test_double_yields_nearest_two_minute(mock_date):
    from datetime import datetime

    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
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

    assert composite.target_minute == 30
# end region

# region Next Day returns nearest next day


def test_empty_composite_throws_next_day():
    composite = AlarmComposite()
    with pytest.raises(Exception) as exc_info:
        composite.next_day
    assert 'Must have at least one alarm' in exc_info.value.args[0]


def test_single_yields_that_next_day():
    composite = AlarmComposite()
    alarm = Alarm()
    composite.add_alarm(alarm)
    alarm.add_target_day(Days.MONDAY)

    assert composite.next_day == Days.MONDAY


def test_double_yields_nearest_next_day(mock_date):
    from datetime import datetime
    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
    composite = AlarmComposite()

    alarm1 = Alarm()
    alarm2 = Alarm()
    composite.add_alarms(alarm1, alarm2)

    alarm1.add_target_day(Days.FRIDAY)
    alarm2.add_target_day(Days.SATURDAY)

    assert composite.next_day == Days.FRIDAY


def test_double_yields_nearest_two_next_day(mock_date):
    from datetime import datetime

    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
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

    assert composite.next_day == Days.MONDAY
# end region

# region Desired brightness yields greatest

def test_empty_composite_returns_0_brightness():
    composite = AlarmComposite()
    assert composite.get_desired_brightness() == 0


def test_single_yields_that_brightness(mock_date):
    from datetime import datetime

    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006

    composite = AlarmComposite()

    alarm = Alarm()
    composite.add_alarm(alarm)
    alarm.add_target_day(Days.SUNDAY)
    alarm.target_hour = 6
    alarm.target_minute = 5

    assert alarm.get_desired_brightness() == composite.get_desired_brightness()


def test_double_yields_nearest_brightness(mock_date):
    from datetime import datetime

    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
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

    assert alarm2.get_desired_brightness() == composite.get_desired_brightness()


def test_double_yields_nearest_two_brightness(mock_date):
    from datetime import datetime

    mock_date.now.return_value = datetime(
        2006, 1, 1, 6, 0)  # 6:00, Sunday, Jan 1st, 2006
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

    assert alarm1.get_desired_brightness() == composite.get_desired_brightness()
# end region


if __name__ == '__main__':
    unittest.main()
