from urllib.request import urlopen
from urllib.parse import quote_plus
import json
import mutagen
import sys


__all__ = [
    "Track"
]

def eprint(*values, **kwargs):
    print(*values, file=sys.stderr, **kwargs)

def get_obj_from(url):
    try:
        return json.loads(urlopen(url).read().decode('utf-8'))
    except Exception as e:
        eprint(type(e), str(e))
        return False


def get_300px_album_art_url(artwork_url):
    return artwork_url.replace('large', 't300x300') if artwork_url else None

def embed_artwork(audio:mutagen.File, artwork_url):
    if artwork_url:
        audio.tags.add(
            mutagen.id3.APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc=u'Cover',
                data=urlopen(artwork_url).read()
            )
        )
    return audio


def set_artist_title(audio:mutagen.File, artist, title):
    frame = mutagen.id3.TIT2(encoding=3)
    frame.append(title)
    audio.tags.add(frame)
    frame = mutagen.id3.TPE1(encoding=3)
    frame.append(artist)
    audio.tags.add(frame)
    return audio


class SoundcloudAPI:
    def __init__(self, client_id=None):
        if client_id:
            self.client_id = client_id
        else:
            from .scrape import fetch_soundcloud_client_id
            self.client_id = fetch_soundcloud_client_id()
            if self.client_id is None:
                raise RuntimeError(
                    'ScLib could not automatically find a public client id. '
                    'This means Soundcloud has changed where the public client id is located. '
                    'Please report this to the package author.'
                )

    def resolve(self, url):
        full_url = "https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}&app_version=1499347238".format(
            url=url,
            client_id=self.client_id
        )
        obj = get_obj_from(full_url)
        if obj['kind'] == 'track':
            return Track(obj=obj, client=self)
        elif obj['kind'] == 'playlist':
            return Playlist(obj=obj, client=self)

    def search(self, query, limit=20, offset=0):
        full_url = 'https://api-v2.soundcloud.com/search?q={query}&client_id={client_id}&limit={limit}&offset={offset}'.format(
            client_id=self.client_id,
            limit=limit,
            offset=offset,
            query=quote_plus(query)
        )
        obj = get_obj_from(full_url)
        return obj['collection']

    def get_tracks(self, *track_ids):
        url = 'https://api-v2.soundcloud.com/tracks?ids={track_ids}&client_id={client_id}'.format(
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

        #additional attributes
        "artist",
        "album",

        # Internal Attributes
        "client",
        'ready'
    ]
    def __init__(self, *, obj=None, client=None):
        assert obj
        assert "id" in obj
        for key in self.__slots__:
            if key in obj:
                self.__setattr__(key, obj[key])
        self.clean_attributes()
        self.client = client
        self.ready = False

    def clean_attributes(self):
        username = self.user['username']
        title = self.title
        if " - " in title:
            parts = title.split("-")
            self.artist = parts[0].strip()
            self.title = parts[-1].strip()
        else:
            self.artist = username


    def write_mp3_to(self, fp):
        try:
            fp.seek(0)
            fp.write(self.fetch_track_mp3())
            fp.seek(0)

            audio = mutagen.File(fp, filename="x.mp3")
            audio.add_tags()
            audio = self.set_mp3_attributes(audio)
            audio = embed_artwork(audio, get_300px_album_art_url(self.artwork_url))
            audio.save(fp, v1=2)
            self.ready = True
            fp.seek(0)
            return fp
        except (TypeError, ValueError) as e:
            eprint('File object passed to "write_mp3_to" must be opened in read/write binary ("wb+") mode')
            raise e

    def get_http_stream_url(self, track_id):
        url = "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}".format(
            track_id=str(track_id),
            client_id=self.client.client_id
        )
        try:
            return get_obj_from(url)['http_mp3_128_url']
        except Exception as e:
            eprint(e)
            return None

    def fetch_track_mp3(self):
        return urlopen(
            get_obj_from(
                "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}".format(
                    track_id=self.id,
                    client_id=self.client.client_id
                )
            )['http_mp3_128_url']
        ).read()

    def set_mp3_attributes(self, audio: mutagen.File):
        frame = mutagen.id3.TIT2(encoding=3)
        frame.append(self.title)
        audio.tags.add(frame)
        frame = mutagen.id3.TPE1(encoding=3)
        frame.append(self.artist)
        audio.tags.add(frame)
        if self.album:
            frame = mutagen.id3.TALB(encoding=3)
            frame.append(self.album)
            audio.tags.add(frame)
            print(self.album)
        return audio

    def to_dict(self):
        ignore_attributes = ['client', 'ready']
        track_dict = {}
        for attr in set(self.__slots__):
            if attr not in ignore_attributes:
                track_dict[attr] = self.__getattribute__(attr)
        return track_dict


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

        "client"
    ]
    RESOLVE_THRESHOLD = 100

    def __init__(self, *, obj=None, client=None):
        assert obj
        assert "id" in obj
        for key in self.__slots__:
            if key in obj:
                self.__setattr__(key, obj[key])
        self.client = client
        self.clean_attributes()

    def clean_attributes(self):
        track_objects = []  # type: [Track] # all completed track objects
        num_tracks = len(self.tracks)
        incomplete_track_ids = []   # tracks that do not have metadata

        while self.tracks and 'title' in self.tracks[0]:       # remove completed track objects
            track_objects.append(Track(obj=self.tracks.pop(0), client=self.client))


        while self.tracks:   # while built tracks are less than all tracks
            incomplete_track_ids.append(self.tracks.pop(0)['id'])
            if len(incomplete_track_ids) == self.RESOLVE_THRESHOLD or not self.tracks:
                new_tracks = self.client.get_tracks(*incomplete_track_ids)
                track_objects.extend([Track(obj=t, client=self.client) for t in new_tracks])
                incomplete_track_ids.clear()
        self.tracks = track_objects

    def __len__(self):
        return int(self.track_count)


    def __iter__(self):
        for track in self.tracks:
            yield track
