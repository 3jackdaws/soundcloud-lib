""" Test async track """
import os
from io import BytesIO

import mutagen
import pytest
import pytest_asyncio

from sclib.asyncio import SoundcloudAPI, Track


TEST_TRACK_URL = 'https://soundcloud.com/mt-marcy/cold-nights'
TEST_TRACK_TITLE = 'cold nights'
TEST_TRACK_ARTIST = 'mt. marcy'


@pytest.fixture(scope='session', name='async_api')
def async_client():
    """ client fixture """
    return SoundcloudAPI()


@pytest_asyncio.fixture(name='test_track')
async def track_fixture(async_api):
    """ Track fixture """
    return await async_api.resolve(TEST_TRACK_URL)


@pytest.mark.asyncio
async def test_resolve_track(async_api:SoundcloudAPI):
    """ test resolve """
    track = await async_api.resolve(TEST_TRACK_URL)
    assert type(track) is Track


@pytest.mark.asyncio
async def test_track_has_correct_attributes(test_track:Track):
    """ test correct attrs """
    assert test_track.title == TEST_TRACK_TITLE
    assert test_track.artist == TEST_TRACK_ARTIST


@pytest.mark.asyncio
async def test_track_accepts_correct_file_objects(async_api):
    """ test correct file objs """
    track = await async_api.resolve(TEST_TRACK_URL)
    filename = os.path.realpath('/tmp/faksjhflaksjfhlaksjfdhlkas.mp3')
    with open(filename, 'wb+') as mp3:
        await track.write_mp3_to(mp3)
    os.remove(filename)

    # Create file then open in rb+
    with open(filename, 'w'):  # pylint: disable=unspecified-encoding
        pass

    with open(filename, 'rb+') as mp3:
        await track.write_mp3_to(mp3)
    os.remove(filename)

    try:
        with open(filename, 'w') as file:  # pylint: disable=unspecified-encoding
            await track.write_mp3_to(file)
    except TypeError:
        pass

    try:
        with open(filename, 'wb') as file:
            await track.write_mp3_to(file)
    except ValueError:
        pass

    file = BytesIO()
    await track.write_mp3_to(file)
    assert file.__sizeof__() > 0


@pytest.mark.asyncio
async def test_track_writes_mp3_metadata(test_track:Track):
    """ test mp3 metadata """
    filename = 'test_track.mp3'
    with open(filename, 'wb+') as file:
        await test_track.write_mp3_to(file)

    mp3 = mutagen.File(filename)
    tags = mp3.tags

    #Check Title and Artist
    assert tags['TIT2'] == TEST_TRACK_TITLE
    assert tags['TPE1'] == TEST_TRACK_ARTIST

    # Check Cover Art
    cover_art = tags['APIC:Cover']  # type: mutagen.id3.APIC
    cover_art_data_actual = cover_art.data
    assert cover_art_data_actual.__sizeof__() > 0
    os.remove(filename)


@pytest.mark.asyncio
async def test_fetch_track_by_id_in_order(async_api: SoundcloudAPI):
    """ Test resolve in order """
    expected = [222820656, 1860005124, 289589592, 268448230]
    tracks = await async_api.get_tracks(*expected)
    actual = [t['id'] for t in tracks]
    assert expected == actual
