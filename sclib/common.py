import mutagen
import sys
from bs4 import BeautifulSoup
import re

def eprint(*values, **kwargs):
    print(*values, file=sys.stderr, **kwargs)

SCRAPE_URLS = [
    'https://soundcloud.com/mt-marcy/cold-nights'
]

class SoundcloudAPI:
    __slots__ = [
        'client_id',
    ]
    resolve_url = "https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
    search_url  = "https://api-v2.soundcloud.com/search?q={query}&client_id={client_id}&limit={limit}&offset={offset}"

    def __init__(self):
        pass

    def get_credentials(self):
        raise NotImplementedError

    def resolve(self, url):
        return NotImplementedError

    def search(self, query):
        return NotImplementedError




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

        # Internal Attributes
        "client",
        "ready"
    ]
    stream_url = "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}"
    def __init__(self, *, obj=None, client=None):
        if not obj:
            raise ValueError("[Track]: obj must not be None")
        if type(client) is not SoundcloudAPI:
            raise ValueError("[Track]: client must be an instance of SoundcloudAPI")

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

    def write_track_metadata(self, track_fp, album_artwork:bytes):
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
            eprint('File object passed to "write_track_metadata" must be opened in read/write binary ("wb+") mode')
            raise e

    def write_mp3_to(self, fp):
        raise NotImplementedError

    def get_stream_url(self):
        raise NotImplementedError


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


def find_script_url(html_text):
    dom = BeautifulSoup(html_text, 'html.parser')
    scripts = dom.findAll('script', attrs={'src': True})
    for script in scripts:
        src = script['src']
        if 'app' in src.split('/')[-1]:
            return src
    return None

def find_client_id(script_text):
    return re.findall(r'client_id:"([a-zA-Z0-9]+)"', script_text)[0]

def get_large_artwork_url(artwork_url):
    return artwork_url.replace('large', 't300x300') if artwork_url else None