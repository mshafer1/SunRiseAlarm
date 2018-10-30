import platform

value = platform.platform()

if 'Windows' in value:
    # this is a no-op class for testing on Windows platforms
    class PWMLED():
        def __init__(self, pin):
            pass
else:
    from gpiozero import PWMLED
