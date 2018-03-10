from sclib.asyncio import SoundcloudAPI, Track
import asyncio

async def fetch_track():
    api = SoundcloudAPI()
    track = await api.resolve('https://soundcloud.com/111h111/home')
    filename = f'{track.artist} - {track.title}.mp3'
    with open('/Users/ian/' + filename, "wb+") as fp:
        await track.write_mp3_to(fp)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(fetch_track())