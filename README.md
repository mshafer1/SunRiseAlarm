# SunRiseAlarm
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
