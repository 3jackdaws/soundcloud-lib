import json
import mutagen
import sys
from bs4 import BeautifulSoup
import random
import re
import aiohttp
import asyncio
import itertools
from . import sync, util

async def get_resource(url) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session as conn:
            async with conn.request('GET', url) as request:
                return await request.content.read()



async def fetch_soundcloud_client_id():
    url = random.choice(util.SCRAPE_URLS)
    page_text = await get_resource(url)
    script_urls = util.find_script_urls(page_text.decode())
    results = await asyncio.gather(*[get_resource(u) for u in script_urls])
    script_text = "".join([r.decode() for r in results])
    print(script_text)
    return util.find_client_id(script_text)

__all__ = [
    "Track",
    "Playlist",
    "SoundcloudAPI"
]

def eprint(*values, **kwargs):
    print(*values, file=sys.stderr, **kwargs)

async def get_obj_from(url):
    try:
        return json.loads(await get_resource(url))
    except Exception as e:
        eprint(type(e), str(e))
        return False




async def embed_artwork(audio:mutagen.File, artwork_url):
    if artwork_url:
        audio.tags.add(
            mutagen.id3.APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc=u'Cover',
                data=await get_resource(artwork_url)
            )
        )
    return audio



class SoundcloudAPI(sync.SoundcloudAPI):

    async def get_credentials(self):
        self.client_id = await fetch_soundcloud_client_id()
        if self.client_id is None:
            raise RuntimeError(
                'ScLib could not automatically find a public client id. '
                'This means Soundcloud has changed where the public client id is located. '
                'Please report this to the package author.'
            )

    async def resolve(self, url):
        if not self.client_id:
            await self.get_credentials()
        full_url = "https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}&app_version=1499347238".format(
            url=url,
            client_id=self.client_id
        )
        obj = await get_obj_from(full_url)
        if obj['kind'] == 'track':
            return Track(obj=obj, client=self)
        elif obj['kind'] == 'playlist':
            playlist = Playlist(obj=obj, client=self)
            await playlist.clean_attributes()
            return playlist

    async def get_tracks(self, *track_ids):
        if not self.client_id:
            await self.get_credentials()

        loop = asyncio.get_event_loop()
        tasks = []
        for url in self._format_get_tracks_urls(track_ids):
            task = loop.create_task(get_obj_from(url))
            tasks.append(task)

        response = await asyncio.gather(*tasks)
        tracks = list(itertools.chain.from_iterable(response))
        tracks = sorted(tracks, key=lambda x: track_ids.index(x['id']))
        return tracks




class Track(sync.Track):

    async def write_mp3_to(self, fp):
        try:
            fp.seek(0)
            stream_url = await self.get_stream_url()
            track_mp3_bytes = await get_resource(stream_url)
            fp.write(track_mp3_bytes)
            fp.seek(0)

            album_artwork = None
            if self.artwork_url:
                album_artwork = await get_resource(
                    util.get_large_artwork_url(
                        self.artwork_url
                    )
                )

            self.write_track_id3(fp, album_artwork)
        except (TypeError, ValueError) as e:
            util.eprint('File object passed to "write_mp3_to" must be opened in read/write binary ("wb+") mode')
            util.eprint(e)
            raise e

    async def get_stream_url(self):
        prog_url = self.get_prog_url()
        stream_response = await get_obj_from(prog_url)
        try:
            return stream_response['url']
        except Exception as e:
            eprint(e)
            return None

    def to_dict(self):
        ignore_attributes = ['client', 'ready']
        track_dict = {}
        for attr in set(self.__slots__):
            if attr not in ignore_attributes:
                track_dict[attr] = self.__getattribute__(attr)

        return track_dict



class Playlist(sync.Playlist):

    RESOLVE_THRESHOLD = 100

    async def clean_attributes(self):
        if self.ready:
            return
        self.ready = True

        track_objects = []  # type: [Track] # all completed track objects
        incomplete_track_ids = []   # tracks that do not have metadata

        while self.tracks and 'title' in self.tracks[0]:       # remove completed track objects
            track_objects.append(Track(obj=self.tracks.pop(0), client=self.client))

        while self.tracks:   # while built tracks are less than all tracks
            incomplete_track_ids.append(self.tracks.pop(0)['id'])
            if len(incomplete_track_ids) == self.RESOLVE_THRESHOLD or not self.tracks:
                new_tracks = await self.client.get_tracks(*incomplete_track_ids)
                track_objects.extend([Track(obj=t, client=self.client) for t in new_tracks])
                incomplete_track_ids.clear()

        for track in track_objects:
            if track not in self.tracks:
                self.tracks.append(track)


    def __len__(self):
        return int(self.track_count)

    async def __aiter__(self):
        await self.clean_attributes()
        for track in self.tracks:
            yield track

    def to_dict(self):
        ignore_attributes = ['client', 'ready']
        playlist_dict = {}
        for attr in set(self.__slots__):
            if attr not in ignore_attributes:
                playlist_dict[attr] = self.__getattribute__(attr)

        return playlist_dict
