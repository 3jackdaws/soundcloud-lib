""" Common utils """
import re
import sys

SCRAPE_URL = "https://soundcloud.com/discover"
RESOLVE_URL = "https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
TRACKS_URL = (
    "https://api-v2.soundcloud.com/tracks?ids={track_ids}&client_id={client_id}"
)
# SEARCH_URL = "https://api-v2.soundcloud.com/search?q={query}&client_id={client_id}&limit={limit}&offset={offset}"
# STREAM_URL = "https://api.soundcloud.com/i1/tracks/{track_id}/streams?client_id={client_id}"
# PROGRESSIVE_URL = "https://api-v2.soundcloud.com/media/soundcloud:tracks:{track_id}/53dc4e74-0414-4ab8-8741-a07ac56c787f/stream/progressive?client_id={client_id}"


def eprint(*values, **kwargs):
    """Print to stderr"""
    print(*values, file=sys.stderr, **kwargs)


def find_script_urls(html_text):
    """Get script url that has client_id in it"""
    return re.findall(
        r'<script crossorigin src="(https://a-v2.sndcdn.com/assets/50-.*?)"></script>',
        html_text,
        flags=re.IGNORECASE,
    )[0]


def find_client_id(script_text):
    """Extract client_id from script"""
    key_data = re.findall(r'client_id:"(.*?)"', script_text, flags=re.IGNORECASE)
    if key_data is not None:
        return key_data[0]

    return False


def get_large_artwork_url(artwork_url):
    """Get 300x300 arwork url"""
    return artwork_url.replace("large", "t300x300") if artwork_url else None
