# SunRiseAlarm
Master: &nbsp; [![Travis CI build badge](https://travis-ci.org/mshafer1/SunRiseAlarm.svg?branch=master)](https://travis-ci.org/mshafer1/SunRiseAlarm) 
[![Coverage Status](https://coveralls.io/repos/github/mshafer1/SunRiseAlarm/badge.svg?branch=master)](https://coveralls.io/github/mshafer1/SunRiseAlarm?branch=master)

CLI: &nbsp; [![Travis CI build badge](https://travis-ci.org/mshafer1/SunRiseAlarm.svg?branch=CLI)](https://travis-ci.org/mshafer1/SunRiseAlarm) 
[![Coverage Status](https://coveralls.io/repos/github/mshafer1/SunRiseAlarm/badge.svg?branch=CLI)](https://coveralls.io/github/mshafer1/SunRiseAlarm?branch=CLI)

&nbsp;

Raspberry PI based sunrise alarm clock

&nbsp;

## Requires
|       Item    |       Reason      |   Setup Instruction   | Required Testing | Required for running |
|   ---         |       ---         |           ---         | --- | ---|
|Pi GPIO module | GPIO output | `pip install pigpio`| | &#x2713;
| tinydb        | Configuration storage|    `pip install tinydb`| &#x2713; | &#x2713;
| tinydb-serialization | Serializing enums for config |    `pip install tinydb-serialization`| &#x2713; | &#x2713;
| py-flags        | Python 3.5 compatible flags enum |    `pip install py-flags`| &#x2713; | &#x2713;
| pytest        | Unit testing |    `pip install pytest`| &#x2713; | 

## Alternative Method:
`pip install -r requirements.txt`

## For unit testing (not on Raspberry Pi)
`pip install -r requirements_test.txt`

## Note
Also, when unit testing on non-windows machines, set the enivorment variable `TEST` to a [truethy](https://docs.python.org/3/library/stdtypes.html#truth-value-testing) value.
