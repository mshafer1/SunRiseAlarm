#!/usr/bin/env python3

from distutils.core import setup

setup(name='SunRiseAlarm',
      version='0.1',
      description='Python based web configured sunrise alarm clock',
      author='mshafer1',
      author_email='',
      url='https://github.com/mshafer1/SunRiseAlarm',
      requires=[
          'gpiozero>=1.4.1',
          'tinydb>=3.11.1',
          'pytest>=3.9.3',
          'tinydb-serialization>=1.0.4',
          'mako>=1.0.7',
          'py-flags>=1.1.2'
      ]
      )
