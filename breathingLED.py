#!/usr/bin/env python3
import time
from LED_controller import LEDController

l = LEDController()

step = 1
StepDelay = .1

def _write(value):
    l.value_raw = value


try:
        while True:
                for dc in range(0, 101, step):   # Increase duty cycle: 0~100
                        _write(dc)
                        print(dc)
                        time.sleep(StepDelay)
                time.sleep(1)
                for dc in range(100, -1, 0-step): # Decrease duty cycle: 100~0
                        print(dc)
                        _write(dc)
                        time.sleep(StepDelay)
                time.sleep(.25)
except KeyboardInterrupt:
        _write(0)
        l.__del__()
        raise
