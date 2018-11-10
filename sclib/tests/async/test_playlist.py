import pytest

from sclib.asyncio import SoundcloudAPI, Playlist

PLAYLIST_URL = 'https://soundcloud.com/chilledcow/sets/hip-hop'
TEST_PLAYLIST = None


@pytest.fixture()
@pytest.mark.asyncio
async def test_playlist():
    global TEST_PLAYLIST
    if not TEST_PLAYLIST:
        TEST_PLAYLIST = await SoundcloudAPI().resolve(PLAYLIST_URL)
    return TEST_PLAYLIST


def test_playlist_size(test_playlist:Playlist):
    assert len(test_playlist) > 0
    assert len(test_playlist) == len(test_playlist.tracks)



