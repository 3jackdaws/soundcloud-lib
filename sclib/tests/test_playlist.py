import pytest
from sclib import SoundcloudAPI, Track, Playlist
from sclib.tests.test_api import api

PLAYLIST_URL = 'https://soundcloud.com/chilledcow/sets/hip-hop'
TEST_PLAYLIST = None


@pytest.fixture()
def test_playlist():
    global TEST_PLAYLIST
    if not TEST_PLAYLIST:
        TEST_PLAYLIST = SoundcloudAPI().resolve(PLAYLIST_URL)
    return TEST_PLAYLIST


def test_playlist_size(test_playlist:Playlist):
    assert len(test_playlist) > 0 and type(len(test_playlist)) is int


def test_playlist_fetch_tracks(test_playlist:Playlist):
    assert len(test_playlist.tracks) is len(test_playlist)
