import pytest

@pytest.fixture
def mock_date(mocker):
    mock = mocker.patch('SunRiseAlarm.utilities.TestableDateTime')
    return mock

