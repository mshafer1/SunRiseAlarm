import platform
import config

value = platform.platform()

if 'Windows' in value:
    # this is a no-op class for testing on Windows platforms
    class PWMLED():
        def __init__(self, pin):
            self.value = 0
else:
    from gpiozero import PWMLED


class LEDController(object):
    def __init__(self):
        self._led = PWMLED(config.LED_pin)
        self._led.value = 0

    def setValue(self, value):
        self._led.value = value

    def getValue(self):
        return self._led.value

    @property
    def percentage(self):
        return self._led.value * 100 // 1  # multiply by 100 and truncate

    @percentage.setter
    def percentage(self, value):
        self._led.value = int(value) / 100
