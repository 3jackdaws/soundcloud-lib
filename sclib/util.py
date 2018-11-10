import mutagen
import sys
from bs4 import BeautifulSoup
import re

def eprint(*values, **kwargs):
    print(*values, file=sys.stderr, **kwargs)

SCRAPE_URLS = [
    'https://soundcloud.com/mt-marcy/cold-nights'
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