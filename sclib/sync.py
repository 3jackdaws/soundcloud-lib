""" Soundcloud api sync objects """
from urllib.request import urlopen
import json
import random
from ssl import SSLContext
from concurrent import futures
import mutagen
from . import util


SSL_VERIFY=True

def get_ssl_setting():
    """ Get ssl context """
    if SSL_VERIFY:
        return None
    return SSLContext()

def get_url(url):
    """ Get url """
    with urlopen(url, context=get_ssl_setting()) as client:
        text = client.read()
    return text

def get_page(url):
    """ get text from url """
    return get_url(url).decode('utf-8')

def get_obj_from(url):
    """ Get object from url """
    try:
        return json.loads(get_page(url))
    except Exception as exc:  # pylint: disable=broad-except
        util.eprint(type(exc), str(exc))
        return False


class UnsupportedFormatError(Exception):
    """ unsupported format """



class SoundcloudAPI:
    """ Soundcloud api client """
    __slots__ = [
        'client_id',
    ]
    RESOLVE_URL = "https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
    SEARCH_URL  = "https://api-v2.soundcloud.com/search?q={query}&client_id={client_id}&limit={limit}&offset={offset}"
    STREAM_URL  = "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}"
    TRACKS_URL  = "https://api-v2.soundcloud.com/tracks?ids={track_ids}&client_id={client_id}"
    PROGRESSIVE_URL = "https://api-v2.soundcloud.com/media/soundcloud:tracks:723290971/53dc4e74-0414-4ab8-8741-a07ac56c787f/stream/progressive?client_id={client_id}"

    TRACK_API_MAX_REQUEST_SIZE = 50

    def __init__(self, client_id=None):
        if client_id:
            self.client_id = client_id
        else:
            self.client_id = None


    def get_credentials(self):
        """ get creds """
        url = random.choice(util.SCRAPE_URLS)
        page_text = get_page(url)
        script_urls = util.find_script_urls(page_text)
        for script in script_urls:
            if not self.client_id:
                if type(script) is str and not "":  # pylint: disable=simplifiable-condition
                    js_text = f'{get_page(script)}'
                    self.client_id = util.find_client_id(js_text)

    def resolve(self, url):
        """ Resolve url """
        if not self.client_id:
            self.get_credentials()
        url = SoundcloudAPI.RESOLVE_URL.format(
            url=url,
            client_id=self.client_id
        )

        obj = get_obj_from(url)
        if obj['kind'] == 'track':
            return Track(obj=obj, client=self)
        if obj['kind'] == 'playlist':
            playlist = Playlist(obj=obj, client=self)
            playlist.clean_attributes()
            return playlist
        return None

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

    def get_tracks(self, *track_ids):
        """ Get a list of track ids """
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
    """ Track object """
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
        self.ready = False
        self.clean_attributes()

    def clean_attributes(self):
        """ clean attrs """
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
    def write_mp3_to(self, file):
        """ Write mp3 data to file """
        try:
            file.seek(0)
            stream_url = self.get_stream_url()
            with urlopen(stream_url,context=get_ssl_setting()) as client:
                data = client.read()
            file.write(data)
            file.seek(0)

            album_artwork = None
            if self.artwork_url:
                with urlopen(util.get_large_artwork_url(self.artwork_url),context=get_ssl_setting()) as client:
                    album_artwork = client.read()

            self.write_track_id3(file, album_artwork)
        except (TypeError, ValueError) as exc:
            util.eprint('File object passed to "write_mp3_to" must be opened in read/write binary ("wb+") mode')
            util.eprint(exc)
            raise exc

    def get_prog_url(self):
        """ Get url """
        for transcode in self.media['transcodings']:
            if transcode['format']['protocol'] == 'progressive':
                return transcode['url'] + "?client_id=" + self.client.client_id
        raise UnsupportedFormatError("As of soundcloud-lib 0.5.0, tracks that are not marked as 'Downloadable' cannot be downloaded because this library does not yet assemble HLS streams.")
#
#   Uses urllib
#
    def get_stream_url(self):
        """ Get stream url """
        prog_url = self.get_prog_url()
        url_response = get_obj_from(prog_url)
        return url_response['url']

    def write_track_id3(self, track_fp, album_artwork:bytes = None):
        """ Write track meta """
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
                        desc='Cover',
                        data=album_artwork
                    )
                )
            audio.save(track_fp, v1=2)
            self.ready = True
            track_fp.seek(0)
            return track_fp
        except (TypeError, ValueError) as exc:
            util.eprint('File object passed to "write_track_metadata" must be opened in read/write binary ("wb+") mode')
            raise exc



class Playlist:
    """ Playlist """
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
        self.tracks = []
        for key in self.__slots__:
            self.__setattr__(key, obj[key] if key in obj else None)
        self.client = client
        self.ready = False

    def clean_attributes(self):
        """ Clean attributes """
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
