import unittest
import os.path
import sys

from SunRiseAlarm.database import DB
from SunRiseAlarm.alarm import Alarm
from SunRiseAlarm import utilities

tests_cleanup_after = True
tests_cleanup_before = False


class DBTest_setup(unittest.TestCase):
    db_name = 'test_db.json'

    def setUp(self):
        if tests_cleanup_before:
            self._cleanup()
        self.db = DB(TestDBCanStoreAlarm.db_name)

    def tearDown(self):
        self.db._close()
        self.db = None
        if tests_cleanup_after:
            self._cleanup()

    @staticmethod
    def _cleanup():
        if os.path.isfile(TestDBCanStoreAlarm.db_name):
            os.remove(TestDBCanStoreAlarm.db_name)


class TestDBCanStoreAlarm(DBTest_setup):
    def testTestDBSingleInsertionBasicAlarm(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY
        self.db.add_alarm(alarm)

    def testTestDBDoubleInsertionSameAlarmUpdatesBasicAlarm(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY
        self.db.add_alarm(alarm)

        self.db.add_alarm(alarm)
        self.assertEqual(len(list(self.db.get_alarms())), 1)

    def testTestDBDoubleInsertionDifferentAlarmAddsAlarm(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY
        self.db.add_alarm(alarm)

        alarm2 = Alarm()
        self.db.add_alarm(alarm2)
        self.assertEqual(len(list(self.db.get_alarms())), 2)


class TestCanReloadAlarms(DBTest_setup):
    def testTestDBSingleCanReload(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY | utilities.Days.FRIDAY
        alarm.target_hour = 6
        alarm.target_minute = 5

        self.db.add_alarm(alarm)

        expected_id = list(self.db.get_alarms())[0].id

        self.db._close()
        self.db._open()

        self.assertEqual(len(self.db.get_alarms()), 1)
        alarm = list(self.db.get_alarms())[0]
        self.assertEqual(alarm.target_days, utilities.Days.MONDAY | utilities.Days.FRIDAY)
        self.assertEqual(alarm.target_hour, 6)
        self.assertEqual(alarm.target_minute, 5)
        self.assertEqual(expected_id, alarm.id)

    def test_dbDoubleReload(self):
        alarm1 = Alarm()
        alarm1.target_days = utilities.Days.MONDAY | utilities.Days.FRIDAY
        alarm1.target_hour = 6
        alarm1.target_minute = 5

        self.db.add_alarm(alarm1)

        expected_id = list(self.db.get_alarms())[0].id

        alarm2 = Alarm()
        alarm2.target_days = utilities.Days.ALL
        self.db.add_alarm(alarm2)
        self.db._close()
        self.db._open()

        self.assertEqual(len(self.db.get_alarms()), 2)
        alarm1 = list(self.db.get_alarms())[0]
        self.assertEqual(alarm1.target_days, utilities.Days.MONDAY | utilities.Days.FRIDAY)
        self.assertEqual(alarm1.target_hour, 6)
        self.assertEqual(alarm1.target_minute, 5)
        self.assertEqual(expected_id, alarm1.id)

        alarm2 = list(self.db.get_alarms())[1]
        self.assertEqual(alarm2.target_days, utilities.Days.ALL)


def _parse_args():
    global tests_cleanup_after, tests_cleanup_before
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dirty', default=False, action='store_true')
    parser.add_argument('--before', default=False, action='store_true')
    ns, args = parser.parse_known_args(namespace=unittest)

    tests_cleanup_after = not ns.dirty
    tests_cleanup_before = ns.before

    return ns, sys.argv[:1] + args


if __name__ == "__main__":
    ns, remaining_args = _parse_args()

    # this invokes unittest when leveltest invoked with -m flag like:
    #    python -m leveltest --level=2 discover --verbose
    unittest.main(argv=remaining_args)
