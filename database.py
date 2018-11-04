import copy
import uuid
from tinydb import TinyDB, Query
import unittest
import os.path
import sys

from alarm import Alarm
import utilities


class DB(object):
    def __init__(self, db_path):
        self.__db_path = db_path
        self._open()

    def _close(self):
        self.db.close()

    def _open(self):
        self.db = TinyDB(self.__db_path, indent=4,
                         cls=utilities.SpecialEncoder #, object_hook=utilities.object_decoder
                         )
        self.table = self.db.table('Alarms')

    def add_alarm(self, alarm):
        if not isinstance(alarm, DBAlarm):
            store_alarm = DBAlarm(alarm)
        else:
            store_alarm = alarm
        alarm = Query()
        matches = self.table.search(alarm.id == store_alarm.id)
        assert len(matches) < 2, "Error, conflicting IDs in database!"
        if len(matches) == 1:
            # already exist in db, call update
            self._update_alarm(store_alarm)
        else:
            self.table.insert(store_alarm.__dict__) # store all values

    def get_alarms(self):
        result = []
        alarms = self.table.all()
        for alarm_dict in alarms:
            stored_alarm = DBAlarm()
            for key in alarm_dict:
                setattr(stored_alarm, key, alarm_dict[key])
            result.append(stored_alarm)
        return result

    def _update_alarm(self, store_alarm):
        if not isinstance(store_alarm, DBAlarm):
            raise Exception("Can only update DBAlarm")
        alarm = Query()
        matches = self.table.search(alarm.id == store_alarm.id)
        assert len(matches) == 1, "Error, did not find exactly one match"
        self.db.update(store_alarm.__dict__, alarm.id == store_alarm.id)


class DBAlarm(Alarm):
    ids = []

    def __init__(self, alarm=None, id=None):

        if alarm is not None:
            Alarm.__init__(self, **alarm.__dict__)
        else:
            alarm = Alarm()
            Alarm.__init__(self, **alarm.__dict__)
        # implicitly call base constructor
        if id:
            self.id = id
        else:
            self.id = DBAlarm.get_id(alarm)

    @staticmethod
    def copy(alarm):
        return copy.deepcopy(alarm)

    @classmethod
    def get_id(cls, alarm):
        value = hash(id(alarm))
        while value in cls.ids:
            value = hash(value) # keep hashing till we find one
            cls.ids.append(value)
        return value



tests_cleanup_after = True
tests_cleanup_before = False


class _DBTest_setup(unittest.TestCase):
    db_name = 'test_db.json'

    def setUp(self):
        if tests_cleanup_before:
            self._cleanup()
        self.db = DB(_TestDBCanStoreAlarm.db_name)

    def tearDown(self):
        self.db._close()
        self.db = None
        if tests_cleanup_after:
            self._cleanup()

    @staticmethod
    def _cleanup():
        if os.path.isfile(_TestDBCanStoreAlarm.db_name):
            os.remove(_TestDBCanStoreAlarm.db_name)


class _TestDBCanStoreAlarm(_DBTest_setup):
    def test_testDBSingleInsertionBasicAlarm(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY
        self.db.add_alarm(alarm)

    def test_testDBDoubleInsertionSameAlarmUpdatesBasicAlarm(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY
        self.db.add_alarm(alarm)

        self.db.add_alarm(alarm)
        self.assertEqual(len(self.db.get_alarms()), 1)

    def test_testDBDoubleInsertionDifferentAlarmAddsAlarm(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY
        self.db.add_alarm(alarm)

        alarm2 = Alarm()
        self.db.add_alarm(alarm2)
        self.assertEqual(len(self.db.get_alarms()), 2)


class _TestCanReloadAlarms(_DBTest_setup):
    def test_testDBSingleCanReload(self):
        alarm = Alarm()
        alarm.target_days = utilities.Days.MONDAY | utilities.Days.FRIDAY
        alarm.target_hour = 6
        alarm.target_minute = 5

        self.db.add_alarm(alarm)
        self.db._close()
        self.db._open()

        self.assertEqual(len(self.db.get_alarms()), 1)
        alarm = self.db.get_alarms()[0]
        self.assertEqual(alarm.target_days, utilities.Days.MONDAY | utilities.Days.FRIDAY)
        self.assertEqual(alarm.target_hour, 6)
        self.assertEqual(alarm.target_minute, 5)





def _parse_args():
    global tests_cleanup_after, tests_cleanup_before
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dirty', default=False, action='store_true')
    parser.add_argument('--before', default=False, action='store_true')
    ns, args = parser.parse_known_args(namespace=unittest)

    tests_cleanup_after = ns.dirty
    tests_cleanup_before = ns.before

    return ns, sys.argv[:1] + args


if __name__ == "__main__":
    ns, remaining_args = _parse_args()

    # this invokes unittest when leveltest invoked with -m flag like:
    #    python -m leveltest --level=2 discover --verbose
    unittest.main(argv=remaining_args)
