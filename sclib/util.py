""" Common utils """
import sys
import re
from bs4 import BeautifulSoup

SC_TRACK_RESOLVE_REGEX = r"^(?:https?:\/\/)soundcloud\.com\/[a-z0-9](?!.*?(-|_){2})[\w-]{1,23}[a-z0-9]\/[^\s]+$"

def eprint(*values, **kwargs):
    """ Print to stderr """
    print(*values, file=sys.stderr, **kwargs)


SCRAPE_URLS = [
    'https://soundcloud.com/mt-marcy/cold-nights'
]

def find_script_urls(html_text):
    """ Get script url that has client_id in it """
    dom = BeautifulSoup(html_text, 'html.parser')
    scripts = dom.findAll('script', attrs={'src': True})
    scripts_list = []
    for script in scripts:
        src = script['src']
        if 'cookielaw.org' not in src:  # filter out cookielaw.org
            scripts_list.append(src)
    return scripts_list


def find_client_id(script_text):
    """ Extract client_id from script """
    client_id = re.findall(r'client_id=([a-zA-Z0-9]+)', script_text)
    if len(client_id) > 0:
        return client_id[0]

    return False

def get_large_artwork_url(artwork_url):
    """ Get 500x500 arwork url """
    return artwork_url.replace('large', 't500x500') if artwork_url else None
