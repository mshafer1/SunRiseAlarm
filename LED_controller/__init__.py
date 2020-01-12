import platform
import math
import os

from SunRiseAlarm import config
from SunRiseAlarm import utilities

value = platform.platform()
test_environ = os.environ['TEST'] if 'TEST' in os.environ else ''

if 'Windows' in value or test_environ:
    # this is a no-op class for testing on Windows platforms
    GPIOLib = utilities._MockController

else:
    #from gpiozero import PWMLED
    import pigpio as GPIOLib


class LEDController(object):
    def __init__(self):
        self._pi = GPIOLib.pi()
        self._pin = config.LED_pin
        self._pi.set_PWM_range(self._pin, 4e3)


        self.value_raw = 0

    def __del__(self):
        # self.value_raw = 0
        self._pi.stop()

    @property
    def value_raw(self):
        _value = self._pi.read(self._pin)
        return _value / 4000 * 255

    @value_raw.setter
    def value_raw(self, value):
        _value = value / 255.0 * 4000
        self._pi.set_PWM_dutycycle(self._pin, _value)

    @property
    def value(self):
        return LEDController._inverse_scale(self.value_raw)

    @value.setter
    def value(self, input):
        self.value_raw = LEDController._scale(input)

    @classmethod
    def _scale(cls, percent):
        # this is a scaling based on desired percentage to 8 bit power for linear brightness
        scaled = .0127 * (percent ** 2) + 1.3027 * percent - 2
        scaled = scaled // 1

        scaled = max(0, scaled) # remove negatives
        scaled = min(255, scaled) # remove high
        return scaled
