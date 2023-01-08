# Soundcloud-lib
This Soundcloud API doesn't require a user-provided client ID to function because it scrapes one from public soundcloud pages.  

![Version](https://img.shields.io/badge/version-0.6.0-blue.svg)

# Features
* Can resolve tracks and playlists from URLs
* Can download and write the MP3 representation of a Track to a file
* Fetches and writes mp3 metadata (Album artist, title, artwork)
* Can fetch entire playlists of tracks
* Asyncio support through `sclib.asyncio`

# Installation
This library is installable as a pip package.
```
pip install soundcloud-lib
```

## Saving an mp3 to a file.
This will write the ID3 tags for album artist, track title AND will embed the album artwork into the mp3.
```python
from sclib import SoundcloudAPI, Track, Playlist

# do not pass a Soundcloud client ID that did not come from this library, but you can save a client_id that this lib found and reuse it
api = SoundcloudAPI()  
track = api.resolve('https://soundcloud.com/itsmeneedle/sunday-morning')

assert type(track) is Track

filename = f'./{track.artist} - {track.title}.mp3'

with open(filename, 'wb+') as file:
    track.write_mp3_to(file)

```


## Fetch a playlist

```python
from sclib import SoundcloudAPI, Track, Playlist

api = SoundcloudAPI()
playlist = api.resolve('https://soundcloud.com/playlist_url')

assert type(playlist) is Playlist

for track in playlist.tracks:
    filename = f'./{track.artist} - {track.title}.mp3'
    with open(filename, 'wb+') as file:
        track.write_mp3_to(file)

```

## Asyncio Support
```python
from sclib.asyncio import SoundcloudAPI, Track

api = SoundcloudAPI()
track = await api.resolve('https://soundcloud.com/user/track')

assert type(track) is Track

filename = f'{track.artist} - {track.title}.mp3'

with open(filename, 'wb+') as file:
    await track.write_mp3_to(file)

```

## Fetch a playlist

```python
from sclib.asyncio import SoundcloudAPI, Track, Playlist

api = SoundcloudAPI()
playlist = await api.resolve('https://soundcloud.com/playlist_url')

assert type(playlist) is Playlist

for track in playlist.tracks:
    filename = f'./{track.artist} - {track.title}.mp3'
    with open(filename, 'wb+') as file:
        await track.write_mp3_to(file)

```

## Write Album Name or Track Number
```python
from sclib import SoundcloudAPI, Track, Playlist

playlist = SoundcloudAPI().resolve("https://soundcloud.com/user/sets/playlist_name")

for track_number, track in enumerate(playlist):
    track.track_no = track_number
    track.album = playlist.title
    with open(f"{track.artist} - {track.title}.mp3", "wb+") as file:
        track.write_mp3_to(file)
```


# Known Limitations

### This library cannot download tracks that are not marked "Downloadable". 
"Downloadable" tracks have an MP3 representation while non-"Downloadable" ones only have HLS representations.  I would like to add HLS assembly to this library in the future.


# Bugs or Features
Please report any and all bugs using the issues tab.

Feel free to request new features too.


# Contributing
Please feel free to submit a PR with your changes.
PRs will only be accepted after a passing build.
You can make sure your changes pass the build stage by running `make lint` and `make test` locally without errors.  Code should be 10/10 quality for linting and all tests should pass.
