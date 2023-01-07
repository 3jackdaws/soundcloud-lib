""" Test sync playlists """

import pytest

from sclib import SoundcloudAPI, Playlist

PLAYLIST_URL = 'https://soundcloud.com/soundcloud-circuits/sets/web-tempo-future-dance-and-electronic'
TEST_PLAYLIST = None


@pytest.fixture(name="playlist")
def test_playlist():
    """ Example playlist fixture """

    return SoundcloudAPI().resolve(PLAYLIST_URL)



def test_playlist_size(playlist: Playlist):
    """ Test that playlist size is correct """
    assert len(playlist) > 0 and type(len(playlist)) is int


def test_playlist_fetch_tracks(playlist: Playlist):
    """ Test that number of tracks matches size of playlist """
    assert len(playlist.tracks) is len(playlist)
