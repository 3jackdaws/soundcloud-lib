# Soundcloud-lib
This is a Soundcloud API library that doesn't require a client ID to function.  It's basic, it can really only fetch tracks and playlists, but doesn't require the user to go through the soundcloud app approval process.

![Version](https://img.shields.io/badge/version-0.4.2-blue.svg)
![Build Status](https://jenkins.isogen.net/buildStatus/icon?job=soundcloud-lib)

# Why
I once applied for API access and was approved.  I used this access for months until it was revoked for some reason and all my emails and new applications were ignored.  I decided to create a library that allows me to do Soundcloud API stuff without an approved application.

# Features
* Supports asyncio
* Does not require a client ID
* Fetches and writes mp3 metadata (Album artist, title, artwork)
* Can fetch entire playlists of tracks

# Installation
This library is installable as a pip package.
```
pip install soundcloud-lib
```

# How
This library uses **programming** and **algorithms** to find a client ID that can be used to access the Soundcloud API.

## Saving an mp3 to a file.
This will write the ID3 tags for album artist, track title AND will embed the album artwork into the mp3.
```python
from sclib import SoundcloudAPI, Track, Playlist

api = SoundcloudAPI()  # never pass a Soundcloud client ID that did not come from this library

track = api.resolve('https://soundcloud.com/itsmeneedle/sunday-morning')

assert type(track) is Track

filename = f'./{track.artist} - {track.title}.mp3'

with open(filename, 'wb+') as fp:
    track.write_mp3_to(fp)

```


## Fetch a playlist

```python
from sclib import SoundcloudAPI, Track, Playlist

api = SoundcloudAPI()
playlist = api.resolve('https://soundcloud.com/playlist_url')

assert type(playlist) is Playlist

for track in playlist.tracks:
    filename = f'./{track.artist} - {track.title}.mp3'
    with open(filename, 'wb+') as fp:
        track.write_mp3_to(fp)

```

## Asyncio Support
```python
from sclib.asyncio import SoundcloudAPI, Track

api = SoundcloudAPI()
track = await api.resolve('https://soundcloud.com/user/track')

assert type(track) is Track

filename = f'{track.artist} - {track.title}.mp3'

with open(filename, 'wb+') as fp:
    await track.write_mp3_to(fp)

```

## Fetch a playlist

```python
from sclib.asyncio import SoundcloudAPI, Track, Playlist

api = SoundcloudAPI()
playlist = await api.resolve('https://soundcloud.com/playlist_url')

assert type(playlist) is Playlist

for track in playlist.tracks:
    filename = f'./{track.artist} - {track.title}.mp3'
    with open(filename, 'wb+') as fp:
        await track.write_mp3_to(fp)

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





# Bugs or Features
Please report any and all bugs using the issues tab.

Feel free to request new features too.


# Contributing
Sure, submit a pull request.
