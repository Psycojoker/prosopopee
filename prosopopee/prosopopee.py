#!/usr/bin/env python

import os
import sys
import json
import yaml
import shutil

from jinja2 import Environment, FileSystemLoader

templates = Environment(loader=FileSystemLoader([os.path.realpath(os.path.join(os.getcwd(), "templates")), os.path.join(os.path.split(os.path.realpath(__file__))[0], "templates")]))
index_template = templates.get_template("index.html")
gallery_index_template = templates.get_template("gallery-index.html")
page_template = templates.get_template("page.html")

DEFAULT_GM_QUALITY = 75

CACHE_VERSION = 1


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

    def thumbnail_needs_to_be_generated(self, source, target, image):
        if not os.path.exists(target):
            return True

        if target not in self.cache:
            return True

        cached_thumbnail = self.cache[target]

        if cached_thumbnail["size"] != os.path.getsize(source) or cached_thumbnail["options"] != image.options:
            return True

        return False

    def cache_thumbnail(self, source, target, image):
        self.cache[target] = {"size": os.path.getsize(source), "options": image.options}

    def __del__(self):
        self.json.dump(self.cache, open(self.cache_file_path, "w"))


CACHE = Cache(json=json)


class Image(object):
    base_dir = ""
    target_dir = ""

    def __init__(self, options):
        # assuming string
        if not isinstance(options, dict):
            name = options
            options = {"name": options}

        self.name = name
        self.quality = options.get("quality", DEFAULT_GM_QUALITY)
        self.options = options.copy()  # used for caching, if it's modified -> regenerate
        del self.options["name"]

    def copy(self):
        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, self.name)

        # XXX doing this DOESN'T improve perf at all (or something like 0.1%)
        # if os.path.exists(target) and os.path.getsize(source) == os.path.getsize(target):
            # print "Skiped %s since the file hasn't been modified based on file size" % source
            # return ""
        shutil.copyfile(source, target)

        print source, "->", target
        return ""

    def generate_thumbnail(self, gm_geometry):
        thumbnail_name = self.name.split(".")
        thumbnail_name[-2] += "-small"
        thumbnail_name = ".".join(thumbnail_name)

        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, thumbnail_name)

        if CACHE.thumbnail_needs_to_be_generated(source, target, self):
            command = "gm convert %s -resize %s -quality %s %s" % (source, gm_geometry, self.quality, target)
            print command
            os.system(command)
            CACHE.cache_thumbnail(source, target, self)
        else:
            print "skiped %s since it's already generated (based on source unchanged size and images options set in your gallery's settings.yaml)" % target

        return thumbnail_name

    def __repr__(self):
        return self.name


def error(test, error_message):
    if test:
        return

    sys.stderr.write(error_message)
    sys.stderr.write("\n")
    sys.stderr.write("Abort.\n")
    sys.exit(1)


def main():
    if os.system("which gm > /dev/null") != 0:
        sys.stderr.write("ERROR: I can't locate the 'gm' binary, I won't be able to resize images, please install the 'graphicsmagick' package.\n")
        sys.exit(1)

    error(os.path.exists(os.path.join(os.getcwd(), "settings.yaml")), "I can't find a settings.yaml in the current working directory")

    settings = yaml.safe_load(open("settings.yaml", "r"))

    error(isinstance(settings, dict), "Your settings.yaml should be a dict")
    error(settings.get("title"), "You should specify a title in your main settings.yaml")

    front_page_galleries_cover = []

    dirs = filter(lambda x: x not in (".", "..") and os.path.isdir(x) and os.path.exists(os.path.join(os.getcwd(), x, "settings.yaml")), os.listdir(os.getcwd()))

    error(dirs, "I can't find at least one directory with a settings.yaml in the current working directory (NOT the settings.yml in your current directory, but a one INSIDE A DIRECTORY in your current working directory), you don't have any gallery?")

    if not os.path.exists("build"):
        os.makedirs("build")

    # XXX recursively merge directories
    if os.path.exists(os.path.join(os.getcwd(), "build", "static")):
        shutil.rmtree(os.path.join(os.getcwd(), "build", "static"))
    shutil.copytree(os.path.join(os.path.split(os.path.realpath(__file__))[0], "static"), os.path.join(os.getcwd(), "build", "static"))

    for gallery in dirs:
        gallery_settings = yaml.safe_load(open(os.path.join(os.getcwd(), gallery, "settings.yaml"), "r"))

        error(isinstance(gallery_settings, dict), "Your %s should be a dict" % (os.path.join(gallery, "settings.yaml")))
        error(gallery_settings.get("title"), "You should specify a title in %s" % (os.path.join(gallery, "settings.yaml")))
        error(gallery_settings.get("cover"), "You should specify a path to a cover picture in %s" % (os.path.join(gallery, "settings.yaml")))

        cover_image_path = os.path.join(gallery, gallery_settings["cover"])

        error(os.path.exists(cover_image_path), "File for %s cover image doesn't exists at %s" % (gallery, cover_image_path))

        gallery_title = gallery_settings["title"]
        gallery_sub_title = gallery_settings.get("sub_title", "")
        gallery_date = gallery_settings["date"] if "date" in gallery_settings else ""

        if gallery_settings.get("public", True):
            front_page_galleries_cover.append({
                "title": gallery_title,
                "link": gallery,
                "sub_title": gallery_sub_title,
                "date": gallery_date,
                "cover": cover_image_path,
            })

        if not os.path.exists(os.path.join("build", gallery)):
            os.makedirs(os.path.join("build", gallery))

        # this should probably be a factory
        Image.base_dir = os.path.join(os.getcwd(), gallery)
        Image.target_dir = os.path.join(os.getcwd(), "build", gallery)

        open(os.path.join("build", gallery, "index.html"), "w").write(gallery_index_template.render(settings=settings, gallery=gallery_settings, Image=Image).encode("Utf-8"))

    front_page_galleries_cover = reversed(sorted(front_page_galleries_cover, key=lambda x: x["date"]))

    if settings.get('menu'):
        for item in settings["menu"]:
            for link in item:
                item_file = link
            error(os.path.exists(os.path.join(os.getcwd(), item_file+".yaml")), "I can't find a "+item_file+".yaml in the current working directory")
            open(os.path.join("build", item_file+".html"), "w").write(page_template.render(settings=settings, pages=yaml.safe_load(open(item_file+".yaml", "r")), galleries=front_page_galleries_cover).encode("Utf-8"))

    Image.base_dir = os.getcwd()
    Image.target_dir = os.path.join(os.getcwd(), "build")

    open(os.path.join("build", "index.html"), "w").write(index_template.render(settings=settings, galleries=front_page_galleries_cover, Image=Image).encode("Utf-8"))



if __name__ == '__main__':
    main()
