from sclib import SoundcloudAPI
import json

def pretty_print(obj:dict):
    print(json.dumps(obj, indent=2))


if __name__ == '__main__':
    api = SoundcloudAPI()
    results = api.search('home resonance')
    for item in results:
        print(f'{item["title"]} - {item["user"]["username"]}')