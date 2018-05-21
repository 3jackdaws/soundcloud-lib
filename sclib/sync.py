from urllib.request import urlopen
import json
from . import common
import random
import io

def get_page(url):
    return urlopen(url).read().decode('utf-8')

def get_obj_from(url):
    try:
        return json.loads(get_page(url))
    except Exception as e:
        common.eprint(type(e), str(e))
        return False





class SoundcloudAPI(common.SoundcloudAPI):
    def __init__(self, client_id=None):
        if client_id:
            self.client_id = client_id

    def get_credentials(self):
        url = random.choice(common.SCRAPE_URLS)
        text = get_page(url)
        script_url = common.find_script_url(text)
        script_text = get_page(script_url)
        self.client_id = common.find_client_id(script_text)

    def resolve(self, url):
        if not self.client_id:
            self.get_credentials()
        url = self.resolve_url.format(
            url=url,
            client_id=self.client_id
        )

        obj = get_obj_from(url)
        if obj['kind'] == 'track':
            return Track(obj=obj, client=self)
        elif obj['kind'] == 'playlist':
            return Playlist(obj=obj, client=self)


class Track(common.Track):

    def write_mp3_to(self, fp):
        try:
            fp.seek(0)
            stream_url = self.get_stream_url()
            fp.write(urlopen(stream_url).read())
            fp.seek(0)

            album_artwork = urlopen(
                common.get_large_artwork_url(
                    self.artwork_url
                )
            ).read()

            fp = self.write_track_metadata(fp, album_artwork)
        except (TypeError, ValueError) as e:
            common.eprint('File object passed to "write_mp3_to" must be opened in read/write binary ("wb+") mode')
            raise e

    def get_stream_url(self):
        return get_obj_from(
            self.stream_url.format(
                track_id=self.id,
                client_id=self.client.client_id
            )
        )


class Playlist(common.Playlist):
    pass