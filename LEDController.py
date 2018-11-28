import platform
import config
import math
import utilities

value = platform.platform()

if 'Windows' in value:
    # this is a no-op class for testing on Windows platforms
    PWMLED = utilities._MockPWM_LED

else:
    #from gpiozero import PWMLED
    import pigpio


class LEDController(object):
    def __init__(self):
        self._pi = pigpio.pi()
        #self._led = PWMLED(config.LED_pin)
        #self._led.value = 0
        #self._led.frequency = 1000

    def __del__(self):
        self.value_raw = 0
        self._pi.stop()
        #self._led.close()
        #self._led = None

    @property
    def value_raw(self):
        return self._pi.read(config.LED_pin)

    @value_raw.setter
    def value_raw(self, value):
        self._pi.set_PWM_dutycycle(config.LED_pin, value)

    @property
    def value(self):
        return LEDController._inverse_scale(self.value_raw)

    @value.setter
    def value(self, input):
        self.value_raw = LEDController._scale(input)

    @classmethod
    def _scale(cls, percent):
        # this is a scaling based on desired percentage to 8 bit power for linear brightness
        eight_bit_val = (.0127 * percent ** 2 + 1.3027 * percent ) // 1.0089

        # scale to [0,1]
        scaled = max(0, scaled) # remove negatives
        scaled = min(255, scaled) # remove high
        return scaled

    @classmethod
    def _inverse_scale(cls, raw):

        result = (math.sqrt(1.307e9 * raw + 169.702e6) -13.027e3) / 254
        return result
