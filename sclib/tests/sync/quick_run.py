from sclib import SoundcloudAPI
import json

def pretty_print(obj:dict):
    print(json.dumps(obj, indent=2))


if __name__ == '__main__':
    class A:
        __slots__ = ['a']

    thing = A()
    thing.a = 10
    print(thing.a)