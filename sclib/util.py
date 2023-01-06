import mutagen
import sys
import re

def eprint(*values, **kwargs):
    print(*values, file=sys.stderr, **kwargs)
def get_large_artwork_url(artwork_url):
    return artwork_url.replace('large', 't300x300') if artwork_url else None


