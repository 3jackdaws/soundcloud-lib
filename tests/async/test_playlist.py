"""
Test async playlist
"""
import pytest_asyncio

from sclib.asyncio import SoundcloudAPI, Playlist

PLAYLIST_URL = 'https://soundcloud.com/soundcloud-circuits/sets/web-tempo-future-dance-and-electronic'
TEST_PLAYLIST = None


@pytest_asyncio.fixture(name='test_playlist')
async def playlist_fixture():
    """ Ex playlist """
    return await SoundcloudAPI().resolve(PLAYLIST_URL)



def test_playlist_size(test_playlist: Playlist):
    """ Test async playlist size """
    assert len(test_playlist) > 0
    test_playlist.clean_attributes()
    assert len(test_playlist) == len(test_playlist.tracks)
