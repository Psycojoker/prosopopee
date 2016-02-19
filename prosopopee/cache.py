import os
import json

CACHE_VERSION = 1

def remove_name(options):
    noname_options = options.copy()
    del noname_options["name"]
    return noname_options

class Cache(object):
    cache_file_path = os.path.join(os.getcwd(), ".prosopopee_cache")

    def __init__(self, json):
        # fix: I need to keep a reference to json because for whatever reason
        # modules are set to None during python shutdown thus totally breaking
        # the __del__ call to save the cache
        # This wonderfully stupid behavior has been fixed in 3.4 (which nobody uses)
        self.json = json
        if os.path.exists(os.path.join(os.getcwd(), ".prosopopee_cache")):
            self.cache = json.load(open(self.cache_file_path, "r"))
        else:
            self.cache = {"version": CACHE_VERSION}

        if "version" not in self.cache or self.cache["version"] != CACHE_VERSION:
            print "info: cache format as changed, prune cache"
            self.cache = {"version": CACHE_VERSION}


    def needs_to_be_generated(self, source, target, options):
        if not os.path.exists(target):
            return True

        if target not in self.cache:
            return True

        cached_picture = self.cache[target]

        if cached_picture["size"] != os.path.getsize(source) or cached_picture["options"] != remove_name(options):
            return True

        return False

    def cache_picture(self, source, target, options):
        self.cache[target] = {"size": os.path.getsize(source), "options": remove_name(options)}

    def __del__(self):
        self.json.dump(self.cache, open(self.cache_file_path, "w"))


CACHE = Cache(json=json)
