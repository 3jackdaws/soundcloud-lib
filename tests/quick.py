from sclib.asyncio import SoundcloudAPI, Track
import asyncio
from io import BytesIO

async def do():
    api = SoundcloudAPI()
    urls = [
        'https://soundcloud.com/mt-marcy/cold-nights'
    ]
    for url in urls:
        track = await api.resolve(url)
        file = BytesIO()
        size = file.__sizeof__()
        await track.write_mp3_to(file)


asyncio.get_event_loop().run_until_complete(do())


