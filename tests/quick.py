from sclib import SoundcloudAPI, Track
from io import BytesIO

api = SoundcloudAPI()
urls = [
    'https://soundcloud.com/nittigritti/lights-nitti-gritti-remix-1'
]
for url in urls:
    track = api.resolve(url)
    file = BytesIO()
    size = file.__sizeof__()
    track.write_mp3_to(file)



