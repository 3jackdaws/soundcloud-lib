from urllib.request import urlopen
import json
from . import util
import random
import io
import mutagen

def get_url(url):
    return urlopen(url).read()

def get_page(url):
    return get_url(url).decode('utf-8')

def get_obj_from(url):
    try:
        return json.loads(get_page(url))
    except Exception as e:
        util.eprint(type(e), str(e))
        return False





class SoundcloudAPI:
    __slots__ = [
        'client_id',
    ]
    RESOLVE_URL = "https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
    SEARCH_URL  = "https://api-v2.soundcloud.com/search?q={query}&client_id={client_id}&limit={limit}&offset={offset}"
    STREAM_URL  = "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}"
    TRACKS_URL  = "https://api-v2.soundcloud.com/tracks?ids={track_ids}&client_id={client_id}"

    def __init__(self, client_id=None):
        if client_id:
            self.client_id = client_id
        else:
            self.client_id = None


    def get_credentials(self):
        url = random.choice(util.SCRAPE_URLS)
        page_text = get_page(url)
        script_url = util.find_script_url(page_text)
        script_text = get_page(script_url)
        self.client_id = util.find_client_id(script_text)

    def resolve(self, url):
        if not self.client_id:
            self.get_credentials()
        url = SoundcloudAPI.RESOLVE_URL.format(
            url=url,
            client_id=self.client_id
        )

        obj = get_obj_from(url)
        if obj['kind'] == 'track':
            return Track(obj=obj, client=self)
        elif obj['kind'] == 'playlist':
            playlist = Playlist(obj=obj, client=self)
            playlist.clean_attributes()
            return playlist

    def get_tracks(self, *track_ids):
        url = self.TRACKS_URL.format(
            track_ids=','.join([str(i) for i in track_ids]),
            client_id=self.client_id
        )
        tracks = get_obj_from(url)
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
            fp.write(urlopen(stream_url).read())
            fp.seek(0)

            album_artwork = urlopen(
                util.get_large_artwork_url(
                    self.artwork_url
                )
            ).read()

            self.write_track_id3(fp, album_artwork)
        except (TypeError, ValueError) as e:
            util.eprint('File object passed to "write_mp3_to" must be opened in read/write binary ("wb+") mode')
            util.eprint(e)
            raise e

#
#   Uses urllib
#
    def get_stream_url(self):
        return get_obj_from(
            self.STREAM_URL.format(
                track_id=self.id,
                client_id=self.client.client_id
            )
        )['http_mp3_128_url']

    def write_track_id3(self, track_fp, album_artwork:bytes):
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
