import platform
import config
import math
import utilities

value = platform.platform()

if "Windows" in value:
    # this is a no-op class for testing on Windows platforms
    GPIOLib = utilities._MockController

else:
    # from gpiozero import PWMLED
    import pigpio as GPIOLib


class LEDController(object):
    def __init__(self):
        self._pi = GPIOLib.pi()
        self._pin = config.LED_pin
        self.value_raw = 0

    def __del__(self):
        self.value_raw = 0
        self._pi.stop()

    @property
    def value_raw(self):
        return self._pi.read(self._pin)

    @value_raw.setter
    def value_raw(self, value):
        self._pi.set_PWM_dutycycle(self._pin, value)

    @property
    def value(self):
        return LEDController._inverse_scale(self.value_raw)

    @value.setter
    def value(self, input):
        self.value_raw = LEDController._scale(input)

    @classmethod
    def _scale(cls, percent):
        # this is a scaling based on desired percentage to 8 bit power for linear brightness
        scaled = 0.0127 * (percent ** 2) + 1.3027 * percent - 2
        scaled = scaled // 1

        scaled = max(0, scaled)  # remove negatives
        scaled = min(255, scaled)  # remove high
        return scaled
