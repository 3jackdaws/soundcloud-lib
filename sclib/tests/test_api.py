import pytest
from sclib import SoundcloudAPI, Track

CLIENT_ID= None

@pytest.fixture(scope='session')
def api():
    global CLIENT_ID
    if CLIENT_ID:
        return SoundcloudAPI(CLIENT_ID)
    else:
        sc = SoundcloudAPI()
        CLIENT_ID = sc.client_id
        return sc

def test_fetch_client_id():
    soundcloud = SoundcloudAPI()
    assert soundcloud.client_id is not None
    global CLIENT_ID
    CLIENT_ID = soundcloud.client_id


