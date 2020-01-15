from .alarm import Alarm

from .utilities import Days


class AlarmComposite(object):
    def __init__(self):
        self.alarms = []

    def add_alarm(self, alarm):
        self.alarms.append(alarm)

    def add_alarms(self, *args):
        for alarm in args:
            self.alarms.append(alarm)

    def remove_alarm(self, alarm):
        self.alarms.remove(alarm)

    @property
    def active(self):
        return any(alarm.active for alarm in self.alarms)

    @property
    def target_days(self):
        result = Days(0)
        for alarm in self.alarms:
            result |= alarm.target_days
        return result

    @property
    def target_hour(self):
        return self._find_nearest_alarm().target_hour

    @property
    def target_minute(self):
        return self._find_nearest_alarm().target_minute

    @property
    def next_day(self):
        return self._find_nearest_alarm().next_day

    def get_desired_brightness(self):
        # return greatest brightness
        if len(self.alarms) == 0:
            return 0

        result = self.alarms[0].get_desired_brightness()
        for alarm in self.alarms:
            temp = alarm.get_desired_brightness()
            if temp > result:
                result = temp
        return result

    @property
    def value(self):
        # return greatest value
        if len(self.alarms) == 0:
            return 0

        result = self.alarms[0].value
        for alarm in self.alarms:
            temp = alarm.value
            if temp > result:
                result = temp
        return result

    def _find_nearest_alarm(self):
        if len(self.alarms) == 0:
            raise Exception("Must have at least one alarm")
        nearest = self.alarms[0]
        for alarm in self.alarms:
            if alarm.target_days != Days(0) and alarm.target_datetime < nearest.target_datetime:
                nearest = alarm
        return nearest

