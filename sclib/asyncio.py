""" Asyncio """

import sys
import random
import json
import re
import itertools
import asyncio
import aiohttp
import mutagen

from . import sync, util

async def get_resource(url) -> bytes:
    """ Get a resource based on url """
    async with aiohttp.ClientSession() as session:
        async with session as conn:
            async with conn.request('GET', url) as request:
                return await request.content.read()



async def fetch_soundcloud_client_id():
    """ Get soundlcoud client id """
    url = random.choice(util.SCRAPE_URLS)
    page_text = await get_resource(url)
    script_urls = util.find_script_urls(page_text.decode())
    results = await asyncio.gather(*[get_resource(u) for u in script_urls])
    script_text = "".join([r.decode() for r in results])
    return util.find_client_id(script_text)

__all__ = [
    "Track",
    "Playlist",
    "SoundcloudAPI"
]

def eprint(*values, **kwargs):
    """ Stderr print """
    print(*values, file=sys.stderr, **kwargs)

async def get_obj_from(url):
    """ Get a json object from a url """
    try:
        return json.loads(await get_resource(url))
    except Exception as exc:  # pylint: disable=broad-except
        eprint(type(exc), str(exc))
        return False




async def embed_artwork(audio:mutagen.File, artwork_url):
    """ Embed an artwork image into a mp3 """
    if artwork_url:
        audio.tags.add(
            mutagen.id3.APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=await get_resource(artwork_url)
            )
        )
    return audio



class SoundcloudAPI(sync.SoundcloudAPI):
    """ Asynchronous Soundcloud API Client """

    async def get_credentials(self):  # pylint: disable=invalid-overridden-method)
        """ Find api credentials  """
        self.client_id = await fetch_soundcloud_client_id()
        if self.client_id is None:
            raise RuntimeError(
                'ScLib could not automatically find a public client id. '
                'This means Soundcloud has changed where the public client id is located. '
                'Please report this to the package author.'
            )

    async def resolve(self, url):  # pylint: disable=invalid-overridden-method
        """ Resolve an api url to a soundcloud object """
        if not self.client_id:
            await self.get_credentials()

        if not re.match(util.SC_TRACK_RESOLVE_REGEX, url):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    url = str(response.real_url)

        full_url = f"https://api-v2.soundcloud.com/resolve?url={url}&client_id={self.client_id}&app_version=1499347238"
        obj = await get_obj_from(full_url)
        if obj['kind'] == 'track':
            return Track(obj=obj, client=self)

        if obj['kind'] in ('playlist', 'system-playlist'):
            playlist = Playlist(obj=obj, client=self)
            await playlist.clean_attributes()
            return playlist

    async def get_tracks(self, *track_ids):  # pylint: disable=invalid-overridden-method
        """ Get a list of tracks from a list of ids """
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
    """ Asynchronous track object """

    async def write_mp3_to(self, file):  # pylint: disable=invalid-overridden-method)
        """ Write the mp3 representation of this track to a file object """
        try:
            file.seek(0)
            stream_url = await self.get_stream_url()
            track_mp3_bytes = await get_resource(stream_url)
            file.write(track_mp3_bytes)
            file.seek(0)

            album_artwork = None
            if self.artwork_url:
                album_artwork = await get_resource(
                    util.get_large_artwork_url(
                        self.artwork_url
                    )
                )

            self.write_track_id3(file, album_artwork)
        except (TypeError, ValueError) as exc:
            util.eprint('File object passed to "write_mp3_to" must be opened in read/write binary ("wb+") mode')
            util.eprint(exc)
            raise exc

    async def get_stream_url(self):  # pylint: disable=invalid-overridden-method
        """ get the stream url for this track """
        prog_url = self.get_prog_url()
        stream_response = await get_obj_from(prog_url)
        try:
            return stream_response['url']
        except Exception as exc:  # pylint: disable=broad-except)
            eprint(exc)
            return None

    def to_dict(self) -> dict:
        """ Conver this track object to a dict """
        ignore_attributes = ['client', 'ready']
        track_dict = {}
        for attr in set(self.__slots__):
            if attr not in ignore_attributes:
                track_dict[attr] = getattr(self, attr)

        return track_dict



class Playlist(sync.Playlist):
    """ Playlist """

    RESOLVE_THRESHOLD = 100

    async def clean_attributes(self): # pylint: disable=invalid-overridden-method
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

    async def __aiter__(self):
        await self.clean_attributes()
        for track in self.tracks:
            yield track

    def to_dict(self):
        """ convert this object to a dict """
        ignore_attributes = ['client', 'ready']
        playlist_dict = {}
        for attr in set(self.__slots__):
            if attr not in ignore_attributes:
                playlist_dict[attr] = getattr(attr)

        return playlist_dict
