# Soundcloud-lib
This is a Soundcloud API library that doesn't require a client ID to function.  It's basic, it can really only fetch tracks and playlists, but doesn't require the user to go through the soundcloud app approval process.

# Why
I once applied for API access and was approved.  I used this access for months until it was revoked for some reason and all my emails and new applications were ignored.  I decided to create a library that allows me to do SOundcloud API stuff without an approved application.

# How
This library uses **programming** and **algorithms** to find a client ID that can be used to access the Soundcloud API.

```python
from sclib import SoundcloudAPI, Track, Playlist

api = SoundcloudAPI()
track = api.resolve('https://soundcloud.com/itsmeneedle/sunday-morning')

assert type(track) is Track
filename = f'./{track.artist} - {track.title}.mp3'
with open(filename, 'wb+') as fp:
    track.write_mp3_to(fp)

```
