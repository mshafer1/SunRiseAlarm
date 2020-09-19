import pathlib

import database
import alarm
import utilities

def test__alarm__db_insert__does_not_throw(temp_db):
    a = alarm.Alarm()
    a.target_days = [utilities.Days.SUNDAY]

    temp_db.add_alarm(a)
