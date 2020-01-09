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
        sc.get_credentials()
        CLIENT_ID = sc.client_id
        return sc

def test_fetch_client_id(api):
    assert api.client_id is not None
    assert len(api.client_id) > 10



