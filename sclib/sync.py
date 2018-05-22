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





class SoundcloudAPI():
    __slots__ = [
        'client_id',
    ]
    RESOLVE_URL = "https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
    SEARCH_URL  = "https://api-v2.soundcloud.com/search?q={query}&client_id={client_id}&limit={limit}&offset={offset}"

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
            # TODO
            return Playlist(obj=obj, client=self)


class Track(util.Track):
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
        if type(client) is not SoundcloudAPI:
            raise ValueError("[Track]: client must be an instance of SoundcloudAPI")

        self.client = client

        for key in self.__slots__:
            if key in obj:
                self.__setattr__(key, obj[key])

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
            self.stream_url.format(
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
            if self.album:
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

    @classmethod
    def get_tracks(self, *track_ids):
        url = 'https://api-v2.soundcloud.com/tracks?ids={track_ids}&client_id={client_id}'.format(
            track_ids=','.join([str(i) for i in track_ids]),
            client_id=self.client.client_id
        )
        tracks = get_obj_from(url)
        tracks = sorted(tracks, key=lambda x: track_ids.index(x['id']))
        return tracks


class Playlist(util.Playlist):
    pass
