""" Test Sync Track object """

import os
from io import BytesIO
from urllib.request import urlopen


import mutagen
import pytest

from sclib.sync import SoundcloudAPI, Track
from sclib.util import get_large_artwork_url

from tests.sync.test_api import sc_client  # pylint: disable=unused-import



TEST_TRACK_URL = 'https://soundcloud.com/mt-marcy/cold-nights'
TEST_TRACK_TITLE = 'cold nights'
TEST_TRACK_ARTIST = 'mt. marcy'


@pytest.fixture(name='test_track')
def track_fixture(sync_api):
    """ Example track """
    sync_api = SoundcloudAPI()
    return sync_api.resolve(TEST_TRACK_URL)




def test_resolve_track(sync_api: SoundcloudAPI):
    """ Test that track can be resolved """
    track = sync_api.resolve(TEST_TRACK_URL)
    assert type(track) is Track

def test_track_has_correct_attributes(test_track:Track):
    """ Test that track has correct attrs """
    assert test_track.title == TEST_TRACK_TITLE
    assert test_track.artist == TEST_TRACK_ARTIST


def test_track_accepts_correct_file_objects(sync_api: SoundcloudAPI):
    """ Test that track accepts correct file handles and accurately reports errors """
    track = sync_api.resolve(TEST_TRACK_URL)
    filename = os.path.realpath('faksjhflaksjfhlaksjfdhlkas.mp3')
    with open(filename, 'wb+') as mp3:
        track.write_mp3_to(mp3)
    os.remove(filename)

    # Create file then open in rb+
    with open(filename, 'w'): # pylint: disable=unspecified-encoding
        pass

    try:
        with open(filename, 'rb+') as mp3:
            track.write_mp3_to(mp3)
    finally:
        os.remove(filename)

    try:
        with open(filename, 'w') as file:  # pylint: disable=unspecified-encoding
            track.write_mp3_to(file)
    except TypeError:
        pass

    try:
        with open(filename, 'wb') as file:
            track.write_mp3_to(file)
    except ValueError:
        pass
    finally:
        os.remove(filename)

    file = BytesIO()
    track.write_mp3_to(file)
    assert file.__sizeof__() > 0


def test_track_writes_mp3_metadata(test_track:Track):
    """ Test that MP3 metadata is written correctly """
    filename = 'test_track.mp3'
    with open(filename, 'wb+') as file:
        test_track.write_mp3_to(file)


    mp3 = mutagen.File(filename)
    tags = mp3.tags

    #Check Title and Artist
    assert tags['TIT2'] == TEST_TRACK_TITLE
    assert tags['TPE1'] == TEST_TRACK_ARTIST

    # Check Cover Art
    cover_art = tags['APIC:Cover']  # type: mutagen.id3.APIC
    cover_art_data_actual = cover_art.data
    with urlopen(get_large_artwork_url(test_track.artwork_url)) as client:
        cover_art_data_expected = client.read()
    assert cover_art_data_actual == cover_art_data_expected
    os.remove(filename)


def test_track_writes_mp3_album(sync_api):
    """ Test that mp3 album is written  """
    track = sync_api.resolve('https://soundcloud.com/if2l/2-months')
    assert type(track) == Track
    track.album = 'Made in Abyss OST'
    track.artist = 'Kevin Pekin'
    track.track_no = ":^)"
    filename = f'{track.artist} - {track.title}.mp3'
    try:
        with open(filename, 'wb+') as file:
            track.write_mp3_to(file)
    finally:
        os.remove(filename)


def test_fetch_track_by_id_in_order(sync_api: SoundcloudAPI):
    """ Test that multiple track ids fetched at the same time are returned in the correct order """
    expected = [ 222820656, 1860005124, 289589592, 268448230]
    tracks = sync_api.get_tracks(*expected)
    actual = [t['id'] for t in tracks]
    assert expected == actual
