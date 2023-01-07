""" Test basic api """

import pytest
from sclib import SoundcloudAPI


@pytest.fixture(scope='session', name="sync_api")
def sc_client():
    """ SC Client """
    api = SoundcloudAPI()
    api.get_credentials()
    return api

def test_fetch_client_id(sync_api: SoundcloudAPI):
    """ Test client id can be fetched """
    assert sync_api.client_id is not None
    assert len(sync_api.client_id) > 10
