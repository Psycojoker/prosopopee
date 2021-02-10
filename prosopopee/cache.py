import json
import logging
import os

from multiprocessing import Manager

from .utils import remove_superficial_options

CACHE_VERSION = 2


logger = logging.getLogger("prosopopee." + __name__)


class Cache:
    cache_file_path = os.path.join(os.getcwd(), ".prosopopee_cache")

    def __init__(self, json):
        # fix: I need to keep a reference to json because for whatever reason
        # modules are set to None during python shutdown thus totally breaking
        # the __del__ call to save the cache
        # This wonderfully stupid behavior has been fixed in 3.4 (which nobody uses)
        self.json = json
        if os.path.exists(os.path.join(os.getcwd(), ".prosopopee_cache")):
            cache = json.load(open(self.cache_file_path, "r"))
        else:
            cache = {"version": CACHE_VERSION}

        if "version" not in cache or cache["version"] != CACHE_VERSION:
            print("info: cache format as changed, prune cache")
            cache = {"version": CACHE_VERSION}

        self.cache = Manager().dict(cache)

    def needs_to_be_generated(self, source, target, options):
        if not os.path.exists(target):
            return True

        if target not in self.cache:
            return True

        cached_picture = self.cache[target]

        if cached_picture["size"] != os.path.getsize(source) or cached_picture[
            "options"
        ] != remove_superficial_options(options):
            return True

        return False

    def cache_picture(self, source, target, options):
        self.cache[target] = {
            "size": os.path.getsize(source),
            "options": remove_superficial_options(options),
        }

    def cache_dump(self):
        self.json.dump(dict(self.cache), open(self.cache_file_path, "w"))


CACHE = Cache(json=json)
