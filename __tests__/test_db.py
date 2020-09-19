import pathlib

import pytest

import database
from alarm import Alarm
import utilities


def test__alarm__db_insert__does_not_throw(temp_db):
    a = Alarm()
    a.target_days = [utilities.Days.SUNDAY]

    temp_db.add_alarm(a)


def test__alarm__db_insert_alarm_already_inserted__calls_db_update(temp_db, mocker):
    alarm = Alarm()
    alarm.target_days = utilities.Days.MONDAY
    temp_db.add_alarm(alarm)
    mock = mocker.patch.object(temp_db, "_update_alarm")

    temp_db.add_alarm(alarm)

    mock.assert_called_with(database.DBAlarm(alarm))


def test__alarm__re_inserting_alarm__updates_rather_than_re_inserting(temp_db):
    # pytest.skip("broken")
    alarm = Alarm()
    alarm.target_days = utilities.Days.MONDAY
    temp_db.add_alarm(alarm)
    alarm.target_days = utilities.Days.SUNDAY

    temp_db.add_alarm(alarm)

    assert len(temp_db.get_alarms()) == 1


def test__alarm__re_inserting_alarm__performs_update(temp_db):
    alarm = Alarm()
    alarm.target_days = utilities.Days.MONDAY
    temp_db.add_alarm(alarm)
    alarm.target_days = utilities.Days.SUNDAY

    temp_db.add_alarm(alarm)

    result = temp_db.get_alarms()[0].target_days
    assert result == utilities.Days.SUNDAY


def test__alarm_already_inserted__add__adds_another_alarm(temp_db):
    alarm = Alarm()
    alarm.target_days = utilities.Days.MONDAY
    temp_db.add_alarm(alarm)

    alarm2 = Alarm()
    alarm2.target_days = utilities.Days.SUNDAY
    temp_db.add_alarm(alarm2)

    assert len(temp_db.get_alarms()) == 2


def test__alarm__db_close_and_repone__returns_same_data(temp_db):
    alarm = Alarm()
    alarm.target_days = utilities.Days.MONDAY | utilities.Days.FRIDAY
    alarm.target_hour = 6
    alarm.target_minute = 5
    temp_db.add_alarm(alarm)
    expected_id = temp_db.get_alarms()[0].id

    temp_db._close()
    temp_db._open()

    reloaded_alarm = temp_db.get_alarms()[0]
    expected_alarm = database.DBAlarm(alarm)
    expected_alarm.id = expected_id
    assert expected_alarm == reloaded_alarm
