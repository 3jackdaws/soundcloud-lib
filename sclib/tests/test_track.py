import pytest
from sclib import SoundcloudAPI, Track
from sclib.lib import get_300px_album_art_url
from sclib.tests.test_api import api
import mutagen
from urllib.request import urlopen
import os
from io import BytesIO
import sys

CLIENT_ID = None
TEST_TRACK = None

TEST_TRACK_URL = 'https://soundcloud.com/mt-marcy/cold-nights'
TEST_TRACK_TITLE = 'cold nights'
TEST_TRACK_ARTIST = 'mt. marcy'




@pytest.fixture()
def test_track():
    global TEST_TRACK
    if not TEST_TRACK:
        sc = SoundcloudAPI()
        TEST_TRACK = sc.resolve(TEST_TRACK_URL)
    return TEST_TRACK



def test_resolve_track(api:SoundcloudAPI):
    track = api.resolve(TEST_TRACK_URL)
    assert type(track) is Track

def test_track_has_correct_attributes(test_track:Track):
    assert test_track.title == TEST_TRACK_TITLE
    assert test_track.artist == TEST_TRACK_ARTIST


def test_track_accepts_correct_file_objects(api):

    track = api.resolve(TEST_TRACK_URL)
    filename = os.path.realpath('faksjhflaksjfhlaksjfdhlkas.mp3')
    with open(filename, 'wb+') as mp3:
        track.write_mp3_to(mp3)
    os.remove(filename)

    # Create file then open in rb+
    with open(filename, 'w'):
        pass

    with open(filename, 'rb+') as mp3:
        track.write_mp3_to(mp3)
    os.remove(filename)

    try:
        with open(filename, 'w') as fp:
            track.write_mp3_to(fp)
    except TypeError:
        pass

    try:
        with open(filename, 'wb') as fp:
            track.write_mp3_to(fp)
    except ValueError:
        pass

    file = BytesIO()
    track.write_mp3_to(file)
    assert file.__sizeof__() > 0


def test_track_writes_mp3_metadata(test_track:Track):
    FILENAME = 'test_track.mp3'
    with open(FILENAME, 'wb+') as fp:
        test_track.write_mp3_to(fp)

    mp3 = mutagen.File(FILENAME)
    tags = mp3.tags

    #Check Title and Artist
    assert tags['TIT2'] == TEST_TRACK_TITLE
    assert tags['TPE1'] == TEST_TRACK_ARTIST

    # Check Cover Art
    cover_art = tags['APIC:Cover']  # type: mutagen.id3.APIC
    cover_art_data_actual = cover_art.data
    cover_art_data_expected = urlopen(get_300px_album_art_url(test_track.artwork_url)).read()
    assert cover_art_data_actual == cover_art_data_expected
    os.remove(FILENAME)





def test_fetch_track_by_id_in_order(api:SoundcloudAPI):
    TRACK_IDS = [222509092, 222820656, 221461805, 222398079, 153576776, 289589592, 268448230,]
    tracks = api.get_tracks(*TRACK_IDS)
    for track in tracks:
        assert track['id'] == TRACK_IDS.pop(0)


def test_recognize_weird_tracks(api:SoundcloudAPI):

    track = api.resolve('https://soundcloud.com/nittigritti/lights-nitti-gritti-remix-1')

    print(track.artist)
    print(track.title)


