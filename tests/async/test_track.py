import os
from io import BytesIO
from urllib.request import urlopen

import mutagen
import pytest

from sclib.asyncio import SoundcloudAPI, Track, Playlist


CLIENT_ID = None
TEST_TRACK = None

TEST_TRACK_URL = 'https://soundcloud.com/mt-marcy/cold-nights'
TEST_TRACK_TITLE = 'cold nights'
TEST_TRACK_ARTIST = 'mt. marcy'

API = None

@pytest.fixture(scope='session')
def api():
    global API
    if not API:
        API = SoundcloudAPI()

    return API

@pytest.mark.asyncio
@pytest.fixture()
async def test_track():
    global TEST_TRACK
    if not TEST_TRACK:
        sc = SoundcloudAPI()
        TEST_TRACK = await sc.resolve(TEST_TRACK_URL)
    return TEST_TRACK


@pytest.mark.asyncio
async def test_resolve_track(api:SoundcloudAPI):
    track = await api.resolve(TEST_TRACK_URL)
    assert type(track) is Track

@pytest.mark.asyncio
async def test_track_has_correct_attributes(test_track:Track):
    assert test_track.title == TEST_TRACK_TITLE
    assert test_track.artist == TEST_TRACK_ARTIST

@pytest.mark.asyncio
async def test_track_accepts_correct_file_objects(api):

    track = await api.resolve(TEST_TRACK_URL)
    filename = os.path.realpath('faksjhflaksjfhlaksjfdhlkas.mp3')
    with open(filename, 'wb+') as mp3:
        await track.write_mp3_to(mp3)
    os.remove(filename)

    # Create file then open in rb+
    with open(filename, 'w'):
        pass

    with open(filename, 'rb+') as mp3:
        await track.write_mp3_to(mp3)
    os.remove(filename)

    try:
        with open(filename, 'w') as fp:
            await track.write_mp3_to(fp)
    except TypeError:
        pass

    try:
        with open(filename, 'wb') as fp:
            await track.write_mp3_to(fp)
    except ValueError:
        pass

    file = BytesIO()
    await track.write_mp3_to(file)
    assert file.__sizeof__() > 0


@pytest.mark.asyncio
async def test_track_writes_mp3_metadata(test_track:Track):
    FILENAME = 'test_track.mp3'
    with open(FILENAME, 'wb+') as fp:
        await test_track.write_mp3_to(fp)

    mp3 = mutagen.File(FILENAME)
    tags = mp3.tags

    #Check Title and Artist
    assert tags['TIT2'] == TEST_TRACK_TITLE
    assert tags['TPE1'] == TEST_TRACK_ARTIST

    # Check Cover Art
    cover_art = tags['APIC:Cover']  # type: mutagen.id3.APIC
    cover_art_data_actual = cover_art.data
    assert cover_art_data_actual.__sizeof__() > 0
    os.remove(FILENAME)




@pytest.mark.asyncio
async def test_fetch_track_by_id_in_order(api:SoundcloudAPI):
    EXPECTED = [222820656, 222398079, 153576776, 289589592, 268448230]
    tracks = await api.get_tracks(*EXPECTED)
    actual = [t['id'] for t in tracks]
    assert EXPECTED == actual

@pytest.mark.asyncio
async def test_recognize_edge_case_urls(api:SoundcloudAPI):
    urls = [
        'https://soundcloud.com/nittigritti/lights-nitti-gritti-remix-1'
    ]
    for url in urls:
        track = await api.resolve(url)
        file = BytesIO()
        size = file.__sizeof__()
        await track.write_mp3_to(file)
        assert file.__sizeof__() > size

@pytest.mark.asyncio
async def test_playlist_resolving(api:SoundcloudAPI):
    playlists = [
        'https://soundcloud.com/greg-montilla/sets/download-1'
    ]
    for playlist in playlists:
        pl = await api.resolve(playlist)  # type: Playlist
        for track in pl.tracks:
            print(track.artist, "-", track.title, ":", track.downloadable)



