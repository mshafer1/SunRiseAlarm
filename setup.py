#!/usr/bin/env python3

from distutils.core import setup

setup(
    name="SunRiseAlarm",
    version="0.1",
    description="Python based web configured sunrise alarm clock",
    author="mshafer1",
    author_email="",
    url="https://github.com/mshafer1/SunRiseAlarm",
    requires=[
        "tinydb>3.11",
        "pytest>3.9",
        "tinydb-serialization>1.0",
        "mako>1.0",
        "py-flags>1.1",
        "pigpio",
    ],
)
