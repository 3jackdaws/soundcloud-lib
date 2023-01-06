import re
import time
from _ast import keyword
from urllib.request import urlopen
from urllib.parse import urlparse
import json
from . import util
import random
import io
import urllib.parse
import mutagen
from concurrent import futures
from ssl import SSLContext
from multiprocessing.pool import ThreadPool as Pool
ssl_verify=True

def get_ssl_setting():
    if ssl_verify:
        return None
    else:
        return SSLContext()

def get_url(url):
    return urlopen(url,context=get_ssl_setting()).read()

def get_page(url):
    return get_url(url).decode('utf-8')

def get_obj_from(url):
    try:
        return json.loads(get_page(url))
    except Exception as e:
        util.eprint(type(e), str(e))
        return False
def run(a):
    a()

class UnsupportedFormatError(Exception): pass



class SoundcloudAPI:
    __slots__ = [
        'client_id',
        'debug',
        'next_client_id_update'
    ]
    RESOLVE_URL = "https://api-v2.soundcloud.com/resolve?url={url}&format=json&client_id={client_id}"
    SEARCH_URL  = "https://api-v2.soundcloud.com/search{typedata}?q={query}&client_id={client_id}&limit={limit}&offset={offset}"
    STREAM_URL  = "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}"
    TRACKS_URL  = "https://api-v2.soundcloud.com/tracks?ids={track_ids}&client_id={client_id}"
    PROGRESSIVE_URL = "https://api-v2.soundcloud.com/media/soundcloud:tracks:723290971/53dc4e74-0414-4ab8-8741-a07ac56c787f/stream/progressive?client_id={client_id}"
    SEARCH_URL = "https://api-v2.soundcloud.com/search{typedata}?q={searchdata}&client_id={client_id}&limit={limit}"
    AUTOCOMPLETE_URL = "https://api-v2.soundcloud.com/search/queries?q={searchdata}&client_id={client_id}"
    USER_URL = "https://api-v2.soundcloud.com/users/{id}?client_id={client_id}&limit=80000"
    USER_TRACK_URL = "https://api-v2.soundcloud.com/users/{id}/tracks?client_id={client_id}&limit=80000"
    USER_PLAYLISTS_URL = "https://api-v2.soundcloud.com/users/{id}/playlists?client_id={client_id}&limit=80000"
    USER_URL = "https://api-v2.soundcloud.com/users/{id}?client_id={client_id}&limit=80000"


    TRACK_API_MAX_REQUEST_SIZE = 50

    def __init__(self, client_id=None, debug: bool=False):
        if client_id:
            self.client_id = client_id
        else:
            self.client_id = None
        self.debug = debug
        self.next_client_id_update = 0


    def get_credentials(self):
        page_text = get_page("https://soundcloud.com/discover")
        js_link = re.findall(r'<script crossorigin src="(https://a-v2.sndcdn.com/assets/50-.*?)"></script>', page_text, flags=re.IGNORECASE)[0]
        page_text = get_page(js_link)
        key_data = re.findall(r'client_id:"(.*?)"', page_text, flags=re.IGNORECASE)
        if key_data:
            self.client_id = key_data[0]
            self.next_client_id_update = int(time.time()) + 300

    def check_last_modified(self):
        now = int(time.time())
        return (not self.client_id) or (now >= self.next_client_id_update)

    def autocomplete(self, query):
        if self.check_last_modified():
            self.get_credentials()
        full_url = SoundcloudAPI.AUTOCOMPLETE_URL.format(
            searchdata=urllib.parse.quote(query),
            client_id=self.client_id
        )
        if self.debug:
            print(full_url)
        mutiobj = get_obj_from(full_url)["collection"]
        rt = []
        for obj in mutiobj:
            rt.append(obj.get('query'))
        return rt

    def search(self, searchdata, tracks:bool=None, limit:int=10):
        if self.check_last_modified():
            self.get_credentials()
        if tracks is None:
            typedata = ""
        elif tracks is False:
            typedata = "/playlists"
        elif tracks is True:
            typedata = "/tracks"
        full_url = SoundcloudAPI.SEARCH_URL.format(
            typedata=typedata,
            searchdata=urllib.parse.quote(searchdata),
            client_id=self.client_id,
            limit=limit
        )
        mutiobj = get_obj_from(full_url)["collection"]
        if self.debug:
            print(full_url)
            print(mutiobj)
        rt = []
        for obj in mutiobj:
            if obj.get('kind') == 'track':
                rt.append(Track(obj=obj, client=self))
            elif obj.get('kind') == 'playlist':
                playlist = Playlist(obj=obj, client=self)
                playlist.clean_attributes()
                rt.append(playlist)
        if len(rt) > 0:
            return rt
        elif len(rt) == 0:
            raise RuntimeError("404 not found !")

    def resolve(self, url):
        if self.check_last_modified():
            self.get_credentials()
        if urlparse(url).hostname.lower() == "on.soundcloud.com":
            url = urlopen(url, context=get_ssl_setting()).url
        full_url = SoundcloudAPI.RESOLVE_URL.format(
            url=url,
            client_id=self.client_id
        )
        obj = get_obj_from(full_url)
        if self.debug:
            print(full_url)
            print(obj)
        if obj.get('kind') == 'track':
            return Track(obj=obj, client=self)
        elif obj.get('kind') == 'playlist':
            playlist = Playlist(obj=obj, client=self)
            playlist.clean_attributes()
            return playlist
        elif obj.get('kind') == 'system-playlist':
            playlist = Playlist(obj=obj, client=self)
            playlist.clean_attributes()
            return playlist
        elif obj.get('kind') == 'user':
            user = USER(obj=obj, client=self)
            user.clean_attributes()
            return user
        else:
            raise RuntimeError("is not playlist or track")

    def _format_get_tracks_urls(self, track_ids):
        urls = []
        for start_offset in range(0, len(track_ids), self.TRACK_API_MAX_REQUEST_SIZE):
            end_offset = start_offset + self.TRACK_API_MAX_REQUEST_SIZE
            track_ids_slice = track_ids[start_offset:end_offset]
            url = self.TRACKS_URL.format(
                track_ids=','.join([str(i) for i in track_ids_slice]),
                client_id=self.client_id
            )
            urls.append(url)
        return urls

    def get_user_track(self, user_id):
        full_url = SoundcloudAPI.USER_TRACK_URL.format(
            id=user_id,
            client_id=self.client_id
        )
        obj = get_obj_from(full_url)["collection"]
        return obj

    def get_user_playlists(self, user_id):
        full_url = SoundcloudAPI.USER_PLAYLISTS_URL.format(
            id=user_id,
            client_id=self.client_id
        )
        obj = get_obj_from(full_url)["collection"]
        return obj

    def get_tracks(self, *track_ids):
        threads = []
        with futures.ThreadPoolExecutor() as executor:
            for url in self._format_get_tracks_urls(track_ids):
                thread = executor.submit(get_obj_from, url)
                threads.append(thread)

        tracks = []
        for thread in futures.as_completed(threads):
            result = thread.result()
            tracks.extend(result)

        tracks = sorted(tracks, key=lambda x: track_ids.index(x['id']))
        return tracks


class Track:
    __slots__ = [
        # Track Attributes
        "artwork_url",
        "artist",
        "commentable",
        "comment_count",
        "created_at",
        "description",
        "downloadable",
        "download_count",
        "download_url",
        "duration",
        "full_duration",
        "embeddable_by",
        "genre",
        "has_downloads_left",
        "id",
        "kind",
        "label_name",
        "last_modified",
        "license",
        "likes_count",
        "media",
        "permalink",
        "permalink_url",
        "playback_count",
        "public",
        "publisher_metadata",
        "purchase_title",
        "purchase_url",
        "release_date",
        "reposts_count",
        "secret_token",
        "sharing",
        "state",
        "streamable",
        "tag_list",
        "title",
        "uri",
        "urn",
        "user_id",
        "visuals",
        "waveform_url",
        "display_date",
        "monetization_model",
        "policy",
        "user",

        #extra attributes
        "album",
        "track_no",

        # Internal Attributes
        "client",
        "ready"
    ]
    STREAM_URL = "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}"
    def __init__(self, *, obj=None, client=None):
        if not obj:
            raise ValueError("[Track]: obj must not be None")
        if not isinstance(client, SoundcloudAPI):
            raise ValueError(f"[Track]: client must be an instance of SoundcloudAPI not {type(client)}")

        for key in self.__slots__:
            self.__setattr__(key, obj[key] if key in obj else None)

        self.client = client
        self.clean_attributes()

    def clean_attributes(self):
        username = self.user['username']
        title = self.title
        if " - " in title:
            parts = title.split("-")
            self.artist = parts[0].strip()
            self.title = "-".join(parts[1:]).strip()
        else:
            self.artist = username
#
#   Uses urllib
#
    def write_mp3_to(self, fp):
        try:
            fp.seek(0)
            stream_url = self.get_stream_url()
            fp.write(urlopen(stream_url,context=get_ssl_setting()).read())
            fp.seek(0)

            album_artwork = None
            if self.artwork_url:
                album_artwork = urlopen(
                    util.get_large_artwork_url(
                        self.artwork_url
                    ),context=get_ssl_setting()
                ).read()

            self.write_track_id3(fp, album_artwork)
        except (TypeError, ValueError) as e:
            util.eprint('File object passed to "write_mp3_to" must be opened in read/write binary ("wb+") mode')
            util.eprint(e)
            raise e

    def get_prog_url(self):
        for transcode in self.media['transcodings']:
            if transcode['format']['protocol'] == 'progressive':
                return transcode['url'] + "?client_id=" + self.client.client_id
        raise UnsupportedFormatError("As of soundcloud-lib 0.5.0, tracks that are not marked as 'Downloadable' cannot be downloaded because this library does not yet assemble HLS streams.")
#
#   Uses urllib
#
    def get_stream_url(self):
        prog_url = self.get_prog_url()
        url_response = get_obj_from(prog_url)
        return url_response['url']

    def write_track_id3(self, track_fp, album_artwork:bytes = None):
        try:
            audio = mutagen.File(track_fp, filename="x.mp3")
            audio.add_tags()

        # SET TITLE
            frame = mutagen.id3.TIT2(encoding=3)
            frame.append(self.title)
            audio.tags.add(frame)
        # SET ARTIST
            frame = mutagen.id3.TPE1(encoding=3)
            frame.append(self.artist)
            audio.tags.add(frame)

        # SET ALBUM
            if self.album:
                frame = mutagen.id3.TALB(encoding=3)
                frame.append(self.album)
                audio.tags.add(frame)
        # SET TRACK NO
            if self.track_no:
                frame = mutagen.id3.TRCK(encoding=3)
                frame.append(str(self.track_no))
                audio.tags.add(frame)
        # SET ARTWORK
            if album_artwork:
                audio.tags.add(
                    mutagen.id3.APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc=u'Cover',
                        data=album_artwork
                    )
                )
            audio.save(track_fp, v1=2)
            self.ready = True
            track_fp.seek(0)
            return track_fp
        except (TypeError, ValueError) as e:
            util.eprint('File object passed to "write_track_metadata" must be opened in read/write binary ("wb+") mode')
            raise e



class Playlist:
    __slots__ = [
        "artwork_url",
        "created_at",
        "description",
        "duration",
        "embeddable_by",
        "genre",
        "id",
        "kind",
        "label_name",
        "last_modified",
        "license",
        "likes_count",
        "managed_by_feeds",
        "permalink",
        "permalink_url",
        "public",
        "purchase_title",
        "purchase_url",
        "release_date",
        "reposts_count",
        "secret_token",
        "sharing",
        "tag_list",
        "title",
        "uri",
        "user_id",
        "set_type",
        "is_album",
        "published_at",
        "display_date",
        "user",
        "tracks",
        "track_count",

        "client",
        "ready"
    ]
    RESOLVE_THRESHOLD = 100

    def __init__(self, *, obj=None, client=None):
        assert obj
        assert "id" in obj
        for key in self.__slots__:
            self.__setattr__(key, obj[key] if key in obj else None)
        self.client = client

    def clean_attributes(self):
        if self.ready:
            return
        self.ready = True
        track_objects = []  # type: [Track] # all completed track objects
        incomplete_track_ids = []  # tracks that do not have metadata

        while self.tracks and 'title' in self.tracks[0]:  # remove completed track objects
            track_objects.append(Track(obj=self.tracks.pop(0), client=self.client))

        while self.tracks:  # while built tracks are less than all tracks
            incomplete_track_ids.append(self.tracks.pop(0)['id'])
            if len(incomplete_track_ids) == self.RESOLVE_THRESHOLD or not self.tracks:
                new_tracks = self.client.get_tracks(*incomplete_track_ids)
                track_objects.extend([Track(obj=t, client=self.client) for t in new_tracks])
                incomplete_track_ids.clear()
        self.tracks = track_objects

    def __len__(self):
        return int(self.track_count)

    def __iter__(self):
        self.clean_attributes()
        for track in self.tracks:
            yield track

class USER:
    __slots__ = [
        "avatar_url",
        "city",
        "comments_count",
        "country_code",
        "created_at",
        "creator_subscriptions",
        "creator_subscription",
        "description",
        "followers_count",
        "followings_count",
        "first_name",
        "full_name",
        "groups_count",
        "id",
        "kind",
        "last_modified",
        "last_name",
        "likes_count",
        "playlist_likes_count",
        "permalink",
        "permalink_url",
        "playlist_count",
        "reposts_count",
        "track_count",
        "uri",
        "urn",
        "username",
        "verified",
        "visuals",
        "badges",
        "station_urn",
        "station_permalink",
        "tracks",
        "playlists",

        "client",
        "ready"
    ]
    RESOLVE_THRESHOLD = 100

    def __init__(self, *, obj=None, client: SoundcloudAPI=None):
        assert obj
        assert "id" in obj
        for key in self.__slots__:
            self.__setattr__(key, obj[key] if key in obj else None)
        self.client = client

    def clean_attributes(self):
        if self.ready:
            return
        self.tracks = self.client.get_user_track(self.id)
        self.playlists = self.client.get_user_playlists(self.id)
        self.ready = True
        track_objects = []  # type: [Track] # all completed track objects
        incomplete_track_ids = []  # tracks that do not have metadata

        while self.tracks and 'title' in self.tracks[0]:  # remove completed track objects
            track_objects.append(Track(obj=self.tracks.pop(0), client=self.client))

        while self.tracks:  # while built tracks are less than all tracks
            incomplete_track_ids.append(self.tracks.pop(0)['id'])
            if len(incomplete_track_ids) == self.RESOLVE_THRESHOLD or not self.tracks:
                new_tracks = self.client.get_tracks(*incomplete_track_ids)
                track_objects.extend([Track(obj=t, client=self.client) for t in new_tracks])
                incomplete_track_ids.clear()
        self.tracks = track_objects
        obj_playlists = []
        def get_playlists_Track(pl):
            plo = Playlist(obj=pl, client=self.client)
            plo.clean_attributes()
            return plo

        threads = []
        with futures.ThreadPoolExecutor() as executor:
            for pl in self.playlists:
                thread = executor.submit(get_playlists_Track, pl)
                threads.append(thread)

        for thread in futures.as_completed(threads):
            result = thread.result()
            obj_playlists.append(result)
        self.playlists = obj_playlists

    def __len__(self):
        return int(self.track_count)

    def __iter__(self):
        self.clean_attributes()
        for track in self.tracks:
            yield track
