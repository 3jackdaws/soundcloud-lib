from sclib import SoundcloudAPI, Track

api = SoundcloudAPI()

track = api.resolve("https://soundcloud.com/modus/shadows-modus-remix")


print(track.artist)