#!/usr/bin/env python

import os
import sys
import yaml
import shutil

from jinja2 import Environment, FileSystemLoader

from .cache import CACHE
from .utils import error

templates = Environment(loader=FileSystemLoader([os.path.realpath(os.path.join(os.getcwd(), "templates")), os.path.join(os.path.split(os.path.realpath(__file__))[0], "templates")]))
index_template = templates.get_template("index.html")
gallery_index_template = templates.get_template("gallery-index.html")
page_template = templates.get_template("page.html")

SETTINGS = {
    "gm": {
        "quality": 75,
        "auto-orient": True
    }
}

class Image(object):
    base_dir = ""
    target_dir = ""

    def __init__(self, options):
        # assuming string
        if not isinstance(options, dict):
            options = {"name": options}
        self.options = options.copy()  # used for caching, if it's modified -> regenerate
        self.options.update(SETTINGS["gm"])

    @property
    def name(self):
        return self.options["name"]

    @property
    def quality(self):
        return self.options["quality"]

    @property
    def autoorient(self):
        return self.options["auto-orient"]

    def copy(self):
        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, self.name)

        # XXX doing this DOESN'T improve perf at all (or something like 0.1%)
        # if os.path.exists(target) and os.path.getsize(source) == os.path.getsize(target):
            # print "Skipped %s since the file hasn't been modified based on file size" % source
            # return ""
        if not self.autoorient:
            shutil.copyfile(source, target)
            print source, "->", target
        else:
            command = "gm convert %s -strip -auto-orient %s" % (source, target)
            print command
            os.system(command)

        return ""

    def generate_thumbnail(self, gm_geometry):
        thumbnail_name = self.name.split(".")
        thumbnail_name[-2] += "-%s" % gm_geometry
        thumbnail_name = ".".join(thumbnail_name)

        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, thumbnail_name)

        if CACHE.thumbnail_needs_to_be_generated(source, target, self):
            gm_options = ""
            if self.autoorient:
                gm_options = "-auto-orient"
            command = "gm convert %s -strip %s -resize %s -quality %s %s" % (source, gm_options, gm_geometry, self.quality, target)
            print command
            os.system(command)
            CACHE.cache_thumbnail(source, target, self)
        else:
            print "skipped %s since it's already generated (based on source unchanged size and images options set in your gallery's settings.yaml)" % target

        return thumbnail_name

    def __repr__(self):
        return self.name


def main():
    if os.system("which gm > /dev/null") != 0:
        sys.stderr.write("ERROR: I can't locate the 'gm' binary, I won't be able to resize images, please install the 'graphicsmagick' package.\n")
        sys.exit(1)

    error(os.path.exists(os.path.join(os.getcwd(), "settings.yaml")), "I can't find a settings.yaml in the current working directory")

    settings = yaml.safe_load(open("settings.yaml", "r"))

    error(isinstance(settings, dict), "Your settings.yaml should be a dict")
    error(settings.get("title"), "You should specify a title in your main settings.yaml")

    if settings.get("settings", {}).get("gm"):
        SETTINGS["gm"].update(settings["settings"]["gm"])

    front_page_galleries_cover = []

    dirs = filter(lambda x: x not in (".", "..") and os.path.isdir(x) and os.path.exists(os.path.join(os.getcwd(), x, "settings.yaml")), os.listdir(os.getcwd()))

    error(dirs, "I can't find at least one directory with a settings.yaml in the current working directory (NOT the settings.yaml in your current directory, but one INSIDE A DIRECTORY in your current working directory), you don't have any gallery?")

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

        if gallery_settings.get("public", True):
            error(gallery_settings.get("title"), "Your galery describe in %s need to have a title" % (os.path.join(gallery, "settings.yaml")))
            error(gallery_settings.get("cover"), "You should specify a path to a cover picture in %s" % (os.path.join(gallery, "settings.yaml")))
            cover_image_path = os.path.join(gallery, gallery_settings["cover"])
            error(os.path.exists(cover_image_path), "File for %s cover image doesn't exist at %s" % (gallery, cover_image_path))

            front_page_galleries_cover.append({
                "title": gallery_settings["title"],
                "link": gallery,
                "sub_title": gallery_settings.get("sub_title", ""),
                "date": gallery_settings.get("date", ""),
                "tags": gallery_settings.get("tags", ""),
                "cover": cover_image_path,
            })

        if not os.path.exists(os.path.join("build", gallery)):
            os.makedirs(os.path.join("build", gallery))

        # this should probably be a factory
        Image.base_dir = os.path.join(os.getcwd(), gallery)
        Image.target_dir = os.path.join(os.getcwd(), "build", gallery)

        template_to_render = page_template if gallery_settings.get("static") else gallery_index_template
        open(os.path.join("build", gallery, "index.html"), "w").write(template_to_render.render(settings=settings, gallery=gallery_settings, Image=Image).encode("Utf-8"))

    front_page_galleries_cover = reversed(sorted(front_page_galleries_cover, key=lambda x: x["date"]))

    # this should probably be a factory
    Image.base_dir = os.getcwd()
    Image.target_dir = os.path.join(os.getcwd(), "build")

    open(os.path.join("build", "index.html"), "w").write(index_template.render(settings=settings, galleries=front_page_galleries_cover, Image=Image).encode("Utf-8"))


if __name__ == '__main__':
    main()
