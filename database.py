import copy
from tinydb import TinyDB, Query
from tinydb_serialization import SerializationMiddleware

from .alarm import Alarm
from . import utilities


class DB(object):
    def __init__(self, db_path):
        self.__db_path = db_path
        self._open()

    def _close(self):
        self.db.close()

    def _open(self):
        serialization = SerializationMiddleware()
        serialization.register_serializer(utilities.DaysSerializer, 'Days')
        self.db = TinyDB(self.__db_path, indent=4, storage=serialization)
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
