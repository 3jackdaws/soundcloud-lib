# Soundcloud-lib
This is a Soundcloud API library that doesn't require a client ID to function.  It's basic, it can really only fetch tracks and playlists, but doesn't require the user to go through the soundcloud app approval process.

# Why
I once applied for API access and was approved.  I used this access for months until it was revoked for some reason and all my emails and new applications were ignored.  I decided to create a library that allows me to do Soundcloud API stuff without an approved application.

# Features
* Does not require a client ID
* Fetches and writes mp3 metadata (Album artist, title, artwork)
* Can fetch entire playlists of tracks

# How
This library uses **programming** and **algorithms** to find a client ID that can be used to access the Soundcloud API.  If you want, you can pass your own client ID as the first argument of `SoundcloudAPI()`.

## Saving an mp3 to a file.
This will write the ID3 tags for album artist, track title AND will embed the album artwork into the mp3.
```python
from sclib import SoundcloudAPI, Track, Playlist

api = SoundcloudAPI()

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

    print(f'Downloading {track.artist} - {track.title}')
    write_mp3_to_file(track)

```

# Bugs or Features
Please report any and all bugs using the issues tab.

Feel free to suggest new features too.


# Contributing
Sure, submit a pull request.