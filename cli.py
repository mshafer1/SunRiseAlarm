#!/usr/bin/env python3
import os

import sys
on_windows = 'linux' not in sys.platform


from database import DB
from alarm import Alarm
from viewModel import ViewModel


def clear_screen():
    command = 'clear'
    if on_windows:
        command = 'cls'
    os.system(command)


def menu(menu_actions):
    keys = list(menu_actions.keys())
    valid_max = len(keys)
    clear_screen()
    while True:

        for i, item in enumerate(keys):
            print("{0}: {1}".format(i + 1, item))
        response = input("Select value [1-{0}]: ".format(len(menu_actions.keys())))
        converted = int(response) - 1
        if 0 <= converted < valid_max:
            menu_actions[keys[converted]]()
        else:
            clear_screen()
            print("Invalid entry, please enter an integer value between 1 and {0}".format(valid_max))


def add_alarm():
    db = DB('alarms.json')
    db.add_alarm(Alarm())


def change_alarm():
    print("Change alarm")


def quit():
    raise QuitException()


class QuitException(Exception):
    pass


if __name__ == '__main__':
    menu_items = {
        "Add Alarm": add_alarm,
        "Quit": quit,
    }
    try:
        vm = ViewModel()

        while True:
            menu(menu_items)
    except:
        vm.__del__()
        raise

