from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import random


SCRAPE_URLS = [
    'https://soundcloud.com/mt-marcy/cold-nights'
]

def fetch_soundcloud_client_id():
    url = random.choice(SCRAPE_URLS)
    page = urlopen(url).read().decode()
    dom = BeautifulSoup(page, 'html.parser')
    scripts = dom.findAll('script', attrs={'src':True})
    for script in scripts:
        src = script['src']
        if 'app' in src.split('/')[-1]:
            app_script_text = urlopen(src).read().decode()
            return re.findall(r'client_id:"([a-zA-Z0-9]+)"', app_script_text)[0]