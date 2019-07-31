# SunRiseAlarm
Master: [![Travis CI build badge](https://travis-ci.org/mshafer1/SunRiseAlarm.svg?branch=master)](https://travis-ci.org/mshafer1/SunRiseAlarm)

[![Coverage Status](https://coveralls.io/repos/github/mshafer1/SunRiseAlarm/badge.svg?branch=master)](https://coveralls.io/github/mshafer1/SunRiseAlarm?branch=master)

CLI: [![Travis CI build badge](https://travis-ci.org/mshafer1/SunRiseAlarm.svg?branch=CLI)](https://travis-ci.org/mshafer1/SunRiseAlarm)

[![Coverage Status](https://coveralls.io/repos/github/mshafer1/SunRiseAlarm/badge.svg?branch=CLI)](https://coveralls.io/github/mshafer1/SunRiseAlarm?branch=CLI)

Raspberry PI based sunrise alarm clock

## Requires
|       Item    |       Reason      |   Setup Instruction   |
|   ---         |       ---         |           ---         |
|Pi GPIO module       | GPIO output | `pip install pigpio`|
| tinydb        | Configuration storage|    `pip install tinydb`|
| tinydb-serialization | Serializing enums for config |    `pip install tinydb-serialization`|
| mako        | Web Server pages |    `pip install mako`|
| py-flags        | Python 3.5 compatible flags enum |    `pip install py-flags`|
| pytest        | Unit testing |    `pip install pytest`|

## Alternative:
`pip install -r requirements.txt`

## For unit testing (not on Raspberry Pi)
`pip install -r requirements_test.txt`
