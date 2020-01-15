import database
import alarmComposite
from alarm import Alarm

import LED_controller
import time
from repeatedTimer import RepeatedTimer


class ViewModel(object):
    def __init__(self):
        self.db = database.DB('alarms.json')
        self.alarms = alarmComposite.AlarmComposite()
        self.led =  LED_controller.LEDController()

        for alarm in self.db.get_alarms():
            self.alarms.add_alarm(alarm)

        self._timer = RepeatedTimer(.1, self._set_brightness)

    def add_alarm(self):
        alarm = Alarm()
        self.db.add_alarm(alarm)
        self.alarms.add_alarm(alarm)
        # TODO: return db ID for alarm.

    def _set_brightness(self):
        brightness = self.alarms.get_desired_brightness()
        self.led.value_raw = brightness
        # print("Setting brightness to: {0}".format(brightness))

    def __del__(self):
        self.led.value = 0
        self._timer.stop()


def _main():

    vm = ViewModel()

    while True:
        pass

if __name__ == '__main__':
    _main()
