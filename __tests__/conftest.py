import os
import sys

import pytest

__MY_PATH = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.realpath(os.path.join(__MY_PATH, "..")))

import database

@pytest.fixture()
def temp_db(tmp_path):
    # tmp_path Pytest fixture provids a per test/run unique folder in the temp directory
    #  it also gets auto-cleaned up after a few runs (usually 3)
    db_file = tmp_path / "db.sqlite"
    db = database.DB(str(db_file))
    yield db

