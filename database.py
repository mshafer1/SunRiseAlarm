import copy
import uuid
from tinydb import TinyDB, Query
import unittest
import os.path

from alarm import Alarm
import utilities



class DB(object):
    def __init__(self, db_path):
        self.db = TinyDB(db_path, indent=4)
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
            self.update_alarm(store_alarm)
        else:
            self.table.insert(store_alarm.__dict__) # store all values

    def get_alarms(self):
        result = []
        alarms = self.table.all()
        for alarm_dict in alarms:
            storedAlarm = DBAlarm({})
            for key in alarm_dict:
                setattr(storedAlarm, key, alarm_dict[key])
            result.append(storedAlarm)
        return result




class DBAlarm(Alarm):
    def __init__(self, base_alarm, id=None):
        # call base constructor
        self.__dict__ = copy.deepcopy(base_alarm.__dict__)
        if id:
            self.id = id
        self.id = uuid.uuid4() # https://docs.python.org/3/library/uuid.html#uuid.uuid4


class _TestDBCanStoreAlarm(unittest.TestCase):
    db_name = 'test_db.json'
    output = utilities._MockPWM_LED()

    def setUp(self):
        self.db = DB(_TestDBCanStoreAlarm.db_name)

    def tearDown(self):
        self.db = None
        if os.path.isfile(_TestDBCanStoreAlarm.db_name):
            os.remove(_TestDBCanStoreAlarm.db_name)

    def test_testDBSingleInsertionBasicAlarm(self):
        alarm = Alarm(_TestDBCanStoreAlarm.output)

        self.db.add_alarm(alarm)

    def test_testDBSingleInsertionBasicAlarm(self):
        alarm = Alarm(_TestDBCanStoreAlarm.output)

        self.db.add_alarm(alarm)


if __name__ == '__main__':
    unittest.main()