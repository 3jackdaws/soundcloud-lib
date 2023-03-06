"""
Test async playlists
"""
import pytest

from sclib.sync import SoundcloudAPI


@pytest.fixture(name='sclib')
def sclib_fixture():
    """ Ex playlist """
    return SoundcloudAPI()


@pytest.mark.parametrize("playlist_url", [
    "https://soundcloud.com/soundcloud-circuits/sets/web-tempo-future-dance-and-electronic",
    "https://soundcloud.com/discover/sets/artist-stations:127466931",
])
def test_playlist_is_resolved(sclib: SoundcloudAPI, playlist_url: str):
    """ Test async playlist is resolved """
    sclib.resolve(playlist_url)


@pytest.mark.parametrize("playlist_url", [
    "https://soundcloud.com/soundcloud-circuits/sets/web-tempo-future-dance-and-electronic",
    "https://soundcloud.com/discover/sets/artist-stations:127466931",
])
def test_playlist_size(sclib: SoundcloudAPI, playlist_url: str):
    """ Test async playlist size """
    test_playlist = sclib.resolve(playlist_url)
    assert len(test_playlist) == len(test_playlist.tracks)


@pytest.mark.parametrize("playlist_url,expected_playlist_kind", [
    ("https://soundcloud.com/soundcloud-circuits/sets/web-tempo-future-dance-and-electronic", "playlist"),
    ("https://soundcloud.com/discover/sets/artist-stations:127466931", "system-playlist"),
])
def test_playlist_type(sclib: SoundcloudAPI, playlist_url: str, expected_playlist_kind: str):
    """ Test async playlist type """
    test_playlist = sclib.resolve(playlist_url)
    assert test_playlist.kind == expected_playlist_kind
