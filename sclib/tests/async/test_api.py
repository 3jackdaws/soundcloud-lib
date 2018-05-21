import pytest
from sclib.asyncio import SoundcloudAPI, Track

API = None

@pytest.fixture(scope='session')
def api():
    global API
    if not API:
        API = SoundcloudAPI()

    return API



