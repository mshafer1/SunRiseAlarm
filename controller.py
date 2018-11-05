import database
import alarmComposite

import LEDController
import time


def _main():
    db = database.DB('alarms.json')
    alarms = alarmComposite.AlarmComposite()
    led = LEDController.LEDController()

    # TODO: register server

    for alarm in db.get_alarms():
        alarms.add_alarm(alarm)

    while True:
        # TODO: handle updates from server (as is, needs to be restarted).
        brightness = alarms.get_desired_brightness()
        led.value = brightness
        print("Setting brightness to: {0}".format(brightness))
        time.sleep(1)


if __name__ == '__main__':
    _main()