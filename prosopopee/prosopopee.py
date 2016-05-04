#!/usr/bin/env python

import os
import sys
import yaml
import shutil

from jinja2 import Environment, FileSystemLoader

from .cache import CACHE
from .utils import error, warning, okgreen

DEFAULTS = {
    "rss": True,
    "share": False,
    "settings": {},
    "show_date": True,
}

SETTINGS = {
    "gm": {
        "quality": 75,
        "auto-orient": True,
        "strip": True,
        "resize": None
    },
    "ffmpeg": {
        "binary": "ffmpeg",
        "loglevel": "panic",
        "format": "webm",
        "resolution": "1280x720",
        "bitrate": "3900k",
        "preselect": "libvpx-720p"
    }
}


class Video(object):
    base_dir = ""
    target_dir = ""

    def __init__(self, options):
        # assuming string
        if not isinstance(options, dict):
            options = {"video": options}
        # used for caching, if it's modified -> regenerate
        self.options = SETTINGS["ffmpeg"].copy()
        self.options.update(options)

    @property
    def name(self):
        return self.options["name"]

    def ffmpeg(self, source, target, options):
        if not CACHE.needs_to_be_generated(source, target, options):
            okgreen("Skipped", source + " is already generated")
            return

        ffmpeg_switches = {
           "source": source,
           "target": target,
           "loglevel": "-loglevel %s" % options["loglevel"],
           "resolution": "-s %s" % options["resolution"],
           "preselect": "-vpre %s" % options["preselect"],
           "resize": "-vf scale=-1:%s" % options.get("resize"),
           "bitrate": "-b %s" % options["bitrate"],
           "format": "-f %s" % options["format"],
           "binary": "%s" % options["binary"]
        }

        warning("Generation", source)

        if options.get("resize"):
            command = "{binary} {loglevel} -i {source} {resize} -vframes 1 -y {target}".format(**ffmpeg_switches)
            print(command)
            os.system(command)
        else:
            command = "{binary} {loglevel} -i {source} {resolution} {preselect} {bitrate} -pass 1 -an {format} -y {target}".format(**ffmpeg_switches)
            command2 = "{binary} {loglevel} -i {source} {resolution} {preselect} {bitrate} -pass 2 -acodec libvorbis -ab 100k {format} -y {target}".format(**ffmpeg_switches)
            print(command)
            os.system(command)
            print(command2)
            os.system(command2)

        CACHE.cache_picture(source, target, options)

    def copy(self):
        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, self.name)
        options = self.options.copy()
        self.ffmpeg(source, target, options)
        return ""

    def generate_thumbnail(self, gm_geometry):
        thumbnail_name = ".".join(self.name.split(".")[:-1] + ["-", gm_geometry, ".png"])

        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, thumbnail_name)

        options = self.options.copy()
        options.update({"resize": gm_geometry})

        self.ffmpeg(source, target, options)

        return thumbnail_name

    def __repr__(self):
        return self.name


class Image(object):
    base_dir = ""
    target_dir = ""

    def __init__(self, options):
        # assuming string
        if not isinstance(options, dict):
            options = {"name": options}
        self.options = SETTINGS["gm"].copy()  # used for caching, if it's modified -> regenerate
        self.options.update(options)

    @property
    def name(self):
        return self.options["name"]

    def gm(self, source, target, options):
        if not CACHE.needs_to_be_generated(source, target, options):
            okgreen("Skipped", source + " is already generated")

        gm_switches = {
           "source": source,
           "target": target,
           "auto-orient": "-auto-orient" if options["auto-orient"] else "",
           "strip": "-strip" if options["strip"] else "",
           "quality": "-quality %s" % options["quality"] if "quality" in options else "-define jpeg:preserve-settings",
           "resize": "-resize %s" % options["resize"] if options.get("resize", None) is not None else ""
        }

        command = "gm convert {source} {auto-orient} {strip} {quality} {resize} {target}".format(**gm_switches)
        warning("Generation", source)

        print(command)
        os.system(command)

        CACHE.cache_picture(source, target, options)

    def copy(self):
        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, self.name)

        # XXX doing this DOESN'T improve perf at all (or something like 0.1%)
        # if os.path.exists(target) and os.path.getsize(source) == os.path.getsize(target):
        # print "Skipped %s since the file hasn't been modified based on file size" % source
        # return ""

        options = self.options.copy()

        if not options["auto-orient"] and not options["strip"]:
            shutil.copyfile(source, target)
            print("%s%s%s" % (source, "->", target))
        else:
            # Do not consider quality settings here, since we aim to copy the input image
            # better to preserve input encoding setting
            del options["quality"]
            self.gm(source, target, options)

        return ""

    def generate_thumbnail(self, gm_geometry):
        thumbnail_name = ".".join(self.name.split(".")[:-1] + ["-", gm_geometry, self.name.split()[-1]])

        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, thumbnail_name)

        options = self.options.copy()
        options.update({"resize": gm_geometry})

        self.gm(source, target, options)

        return thumbnail_name

    def __repr__(self):
        return self.name


def main():
    settings = yaml.safe_load(open("settings.yaml", "r"))
    if settings["settings"].get("ffmpeg"):
        SETTINGS["ffmpeg"].update(settings["settings"]["ffmpeg"])
        conv_video = settings["settings"]["ffmpeg"]["binary"]
    else:
        conv_video = "ffmpeg"

    for i in ['gm', conv_video]:
        if os.system("which " + i +" > /dev/null") != 0:
            sys.stderr.write("ERROR: I can't locate the "+ i +" binary, "
                             "please install the '" + i + "' package.\n")
            sys.exit(1)

    error(os.path.exists(os.path.join(os.getcwd(), "settings.yaml")), "I can't find a "
          "settings.yaml in the current working directory")


    for key, value in DEFAULTS.items():
        if key not in settings:
            settings[key] = value

    error(isinstance(settings, dict), "Your settings.yaml should be a dict")
    error(settings.get("title"), "You need to specify a title in your main settings.yaml")

    if (settings["rss"] or settings["share"]) and not settings.get("url"):
        warning("warning", "If you want the rss and/or the social network share to work, "
                "you need to specify the website url in root settings")
        settings["rss"] = False
        settings["share"] = False

    if settings["settings"].get("gm"):
        SETTINGS["gm"].update(settings["settings"]["gm"])

    front_page_galleries_cover = []

    dirs = filter(lambda x: x not in (".", "..") and os.path.isdir(x) and os.path.exists(os.path.join(os.getcwd(), x, "settings.yaml")), os.listdir(os.getcwd()))

    error(dirs, "I can't find at least one directory with a settings.yaml in the current working "
          "directory (NOT the settings.yaml in your current directory, but one INSIDE A "
          "DIRECTORY in your current working directory), you don't have any gallery?")

    if not os.path.exists("build"):
        os.makedirs("build")

    theme = settings["settings"].get("theme", "exposure")

    theme_path = os.path.exists(os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes", theme))
    available_themes = theme, "', '".join(os.listdir(os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes")))

    error(theme_path, "'%s' is not an existing theme, available themes are '%s'" % (available_themes))

    prosopopee_templates_dir = os.path.realpath(os.path.join(os.getcwd(), "templates"))
    project_templates_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes", theme, "templates")

    templates = Environment(loader=FileSystemLoader([
        prosopopee_templates_dir,
        project_templates_dir
        ]))

    index_template = templates.get_template("index.html")
    gallery_index_template = templates.get_template("gallery-index.html")
    page_template = templates.get_template("page.html")
    feed_template = templates.get_template("feed.xml")

    # XXX recursively merge directories
    if os.path.exists(os.path.join(os.getcwd(), "build", "static")):
        shutil.rmtree(os.path.join(os.getcwd(), "build", "static"))

    if os.path.exists(os.path.join(os.getcwd(), "static")):
        shutil.copytree(os.path.join(os.getcwd(), "static"), os.path.join(os.getcwd(), "build", "static"))
    else:
        shutil.copytree(os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes", theme, "static"), os.path.join(os.getcwd(), "build", "static"))

    for gallery in dirs:
        gallery_settings = yaml.safe_load(open(os.path.join(os.getcwd(), gallery, "settings.yaml"), "r"))

        error(isinstance(gallery_settings, dict), "Your %s should be a dict" % (os.path.join(gallery, "settings.yaml")))
        error(gallery_settings.get("title"), "You should specify a title in %s" % (os.path.join(gallery, "settings.yaml")))

        if gallery_settings.get("public", True):
            error(gallery_settings.get("title"), "Your gallery describe in %s need to have a "
                  "title" % (os.path.join(gallery, "settings.yaml")))
            error(gallery_settings.get("cover"), "You should specify a path to a cover picture "
                  "in %s" % (os.path.join(gallery, "settings.yaml")))
            cover_image_path = os.path.join(gallery, gallery_settings["cover"])
            error(os.path.exists(cover_image_path), "File for %s cover image doesn't exist at "
                  "%s" % (gallery, cover_image_path))

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
        Video.base_dir = os.path.join(os.getcwd(), gallery)
        Video.target_dir = os.path.join(os.getcwd(), "build", gallery)

        template_to_render = page_template if gallery_settings.get("static") else gallery_index_template
        open(os.path.join("build", gallery, "index.html"), "w").write(template_to_render.render(settings=settings, gallery=gallery_settings, Image=Image, Video=Video, link=gallery).encode("Utf-8"))

        if settings["rss"]:
            open(os.path.join("build", "feed.xml"), "w").write(feed_template.render(settings=settings, link=gallery, galleries=reversed(sorted(front_page_galleries_cover, key=lambda x: x["date"]))).encode("Utf-8"))

    front_page_galleries_cover = reversed(sorted(front_page_galleries_cover, key=lambda x: x["date"]))

    # this should probably be a factory
    Image.base_dir = os.getcwd()
    Image.target_dir = os.path.join(os.getcwd(), "build")

    open(os.path.join("build", "index.html"), "w").write(index_template.render(settings=settings, galleries=front_page_galleries_cover, Image=Image).encode("Utf-8"))


if __name__ == '__main__':
    main()
