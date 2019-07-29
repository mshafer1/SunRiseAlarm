#!/usr/bin/env python3
# import RPi.GPIO as GPIO
import pigpio as GPIOLib
import time

_pi = GPIOLib.pi()
LedPin = 18 # physical pin 12 on RasPi-0w
StepDelay = .1

def _write(value):
    _pi.set_PWM_dutycycle(LedPin, value)



# GPIO.setmode(GPIO.BOARD)       # Numbers pins by physical location
# GPIO.setup(LedPin, GPIO.OUT)   # Set pin mode as output
# GPIO.output(LedPin, GPIO.LOW)  # Set pin to low(0V)

# p = GPIO.PWM(LedPin, 1000)     # set Frequece to 1KHz
# p.start(0)                     # Start PWM output, Duty Cycle = 0

try:
        while True:
                for dc in range(0, 101, 5):   # Increase duty cycle: 0~100
                        _write(dc)
                        # print(dc)
                        # p.ChangeDutyCycle(dc)     # Change duty cycle
                        time.sleep(StepDelay)
                time.sleep(1)
                for dc in range(100, -1, -5): # Decrease duty cycle: 100~0
                        # print(dc)
                        # p.ChangeDutyCycle(dc)
                        _write(dc)
                        time.sleep(StepDelay)
                time.sleep(.25)
except KeyboardInterrupt:
        _write(0)
        _pi.stop()
        raise
        # p.stop()
        # GPIO.output(LedPin, GPIO.HIGH)    # turn off all leds
        # GPIO.cleanup()

