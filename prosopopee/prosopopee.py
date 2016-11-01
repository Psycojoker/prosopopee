#!/usr/bin/env python

import os
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
        "resize": None,
        "progressive": True
    },
    "ffmpeg": {
        "binary": "ffmpeg",
        "loglevel": "error",
        "format": "webm",
        "resolution": "1280x720",
        "vbitrate": "3900k",
        "abitrate": "100k",
        "audio": "libvorbis",
        "video": "libvpx",
        "other": "-qmin 10 -qmax 42 -maxrate 500k -bufsize 1500k"
    }
}


class Video(object):
    base_dir = ""
    target_dir = ""

    def __init__(self, options):
        error(SETTINGS["ffmpeg"] is not False, "I couldn't find a binary to convert video and I ask to do so, abort")

        # assuming string
        if not isinstance(options, dict):
            options = {"name": options}
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
           "resize": "-vf scale=-1:%s" % options.get("resize"),
           "vbitrate": "-b:v %s" % options["vbitrate"],
           "abitrate": "-b:v %s" % options["abitrate"],
           "format": "-f %s" % options["format"],
           "binary": "%s" % options["binary"],
           "video": "-c:v %s" % options["video"],
           "audio": "-c:a %s" % options["audio"],
           "other": "%s" % options["other"]
        }

        warning("Generation", source)

        if options.get("resize"):
            command = "{binary} {loglevel} -i {source} {resize} -vframes 1 -y {target}".format(**ffmpeg_switches)
            print(command)
            error(os.system(command) == 0, "%s command failed" % ffmpeg_switches["binary"])
        else:
            command = "{binary} {loglevel} -i {source} {video} {vbitrate} {other} {audio} {abitrate} {resolution} {format} -y {target}".format(**ffmpeg_switches)
            print(command)
            error(os.system(command) == 0, "%s command failed" % ffmpeg_switches["binary"])

        CACHE.cache_picture(source, target, options)

    def copy(self):
        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, self.name)
        options = self.options.copy()
        self.ffmpeg(source, target, options)
        return ""

    def generate_thumbnail(self, gm_geometry):
        thumbnail_name = ".".join(self.name.split(".")[:-1]) + "-%s.png" % gm_geometry

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
            return

        gm_switches = {
           "source": source,
           "target": target,
           "auto-orient": "-auto-orient" if options["auto-orient"] else "",
           "strip": "-strip" if options["strip"] else "",
           "quality": "-quality %s" % options["quality"] if "quality" in options else "-define jpeg:preserve-settings",
           "resize": "-resize %s" % options["resize"] if options.get("resize", None) is not None else "",
           "progressive": "-interlace Line" if options.get("progressive", None) is True else ""
        }

        command = "gm convert '{source}' {auto-orient} {strip} {progressive} {quality} {resize} '{target}'".format(**gm_switches)
        warning("Generation", source)

        print(command)
        error(os.system(command) == 0, "gm command failed")

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
        thumbnail_name = ".".join(self.name.split(".")[:-1]) + "-" + gm_geometry + "." + self.name.split(".")[-1]

        source, target = os.path.join(self.base_dir, self.name), os.path.join(self.target_dir, thumbnail_name)

        options = self.options.copy()
        options.update({"resize": gm_geometry})

        self.gm(source, target, options)

        return thumbnail_name

    def __repr__(self):
        return self.name


def init():
    error(os.path.exists(os.path.join(os.getcwd(), "settings.yaml")), "I can't find a "
          "settings.yaml in the current working directory")

    settings = yaml.safe_load(open("settings.yaml", "r"))

    error(isinstance(settings, dict), "Your settings.yaml should be a dict")

    for key, value in DEFAULTS.items():
        if key not in settings:
            settings[key] = value

    if settings["settings"].get("ffmpeg"):
        SETTINGS["ffmpeg"].update(settings["settings"]["ffmpeg"])

        conv_video = settings["settings"]["ffmpeg"]["binary"]
    else:
        conv_video = "ffmpeg"

    error(os.system("which gm > /dev/null") == 0, "I can't locate the gm binary, "
          "please install the 'graphicsmagick' package.\n")

    if os.system("which " + conv_video + " > /dev/null") != 0:
        if conv_video == "ffmpeg" and os.system("which avconv > /dev/null") == 0:
            SETTINGS["ffmpeg"]["binary"] = "avconv"
            warning("Video", "I couldn't locate ffmpeg but I could find avconv, "
                             "switching to avconv for video conversion")
        else:
            warning("Video", "I can't locate the " + conv_video + " binary, "
                    "please install the '" + conv_video + "' package.\n")
            warning("Video", "I won't be able to encode video and I will stop if I encounter a video to convert")
            SETTINGS["ffmpeg"] = False

    error(settings.get("title"), "You need to specify a title in your main settings.yaml")

    if (settings["rss"] or settings["share"]) and not settings.get("url"):
        warning("warning", "If you want the rss and/or the social network share to work, "
                "you need to specify the website url in root settings")
        settings["rss"] = False
        settings["share"] = False

    if settings["settings"].get("gm"):
        SETTINGS["gm"].update(settings["settings"]["gm"])
    return settings


def get_gallery_templates(theme, gallery_path="", parent_templates=None):
    if theme:
        theme_path = os.path.exists(
            os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes", theme))
        available_themes = theme, "', '".join(
            os.listdir(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                    "themes")))

        error(theme_path, "'%s' is not an existing theme, available themes are '%s'" % available_themes)

        templates_dir = [
            os.path.realpath(os.path.join(os.getcwd(), "templates")),
            os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes", theme, "templates")
        ]

        if theme != "exposure":
            templates_dir.append(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                              "themes", "exposure", "templates"))

        subgallery_templates = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)
    else:
        if parent_templates:
            theme = "exposure"
            subgallery_templates = parent_templates
        else:
            templates_dir = [
                os.path.realpath(os.path.join(os.getcwd(), "templates")),
                os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes", theme, "templates")
            ]
            subgallery_templates = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True)

    # XXX recursively merge directories
    if os.path.exists(os.path.join(os.getcwd(), "build", gallery_path, "static")):
        shutil.rmtree(os.path.join(os.getcwd(), "build", gallery_path, "static"))

    if os.path.exists(os.path.join(os.getcwd(), "static")):
        shutil.copytree(os.path.join(os.getcwd(), "static"), os.path.join(os.getcwd(), "build", gallery_path, "static"))
    else:
        shutil.copytree(
            os.path.join(os.path.split(os.path.realpath(__file__))[0], "themes", theme, "static"),
            os.path.join(os.getcwd(), "build", gallery_path, "static"))
    return subgallery_templates


def process_directory(gallery_name, settings, parent_templates, parent_gallery_path=False):
    if parent_gallery_path:
        gallery_path = os.path.join(parent_gallery_path, gallery_name)
    else:
        gallery_path = gallery_name

    gallery_settings = yaml.safe_load(open(os.path.join(os.getcwd(), gallery_path, "settings.yaml"), "r"))

    error(isinstance(gallery_settings, dict), "Your %s should be a dict" % (os.path.join(gallery_name, "settings.yaml")))
    error(gallery_settings.get("title"), "You should specify a title in %s" % (os.path.join(gallery_name, "settings.yaml")))

    gallery_cover = {}

    sub_galleries = filter(lambda x: x not in (".", "..") and os.path.isdir(os.path.join(gallery_path, x)) and
                  os.path.exists(os.path.join(os.getcwd(), gallery_path, x, "settings.yaml")),
                  os.listdir(os.path.join(os.getcwd(), gallery_path)))

    if not os.path.exists(os.path.join("build", gallery_path)):
            os.makedirs(os.path.join("build", gallery_path))


    if not gallery_settings.get("public", True):
        build_gallery(settings, gallery_settings, gallery_path, parent_templates)
    else:
        gallery_cover = create_cover(gallery_name, gallery_settings, gallery_path)

        if sub_galleries:
            error(gallery_settings.get("sections") is not False,
                  "The gallery in %s can't have both sections and subgalleries" % (os.path.join(gallery_name,
                                                                                                "settings.yaml")))

            # Sub galleries found, create index with them instead of a gallery
            theme = gallery_settings.get("theme", settings.get("theme", "exposure"))

            subgallery_templates = get_gallery_templates(theme, gallery_path, parent_templates)
            sub_page_galleries_cover = []

            for subgallery in sub_galleries:
                sub_page_galleries_cover.append(
                    process_directory(subgallery, settings, subgallery_templates, gallery_path)
                )

            build_index(settings, sub_page_galleries_cover, subgallery_templates, gallery_path)
            gallery_cover['sub_gallery'] = sub_page_galleries_cover
        else:
            # No sub galleries found, create a gallery
            build_gallery(settings, gallery_settings, gallery_path, parent_templates)

    return gallery_cover


def create_cover(gallery_name, gallery_settings, gallery_path):
    error(gallery_settings.get("title"), "Your gallery describe in %s need to have a "
                                         "title" % (os.path.join(gallery_name, "settings.yaml")))

    error(gallery_settings.get("cover"), "You should specify a path to a cover picture "
                                         "in %s" % (os.path.join(gallery_name, "settings.yaml")))

    if isinstance(gallery_settings["cover"], dict):
        cover_image_path = os.path.join(gallery_path, gallery_settings["cover"]["name"])
        cover_image_url = os.path.join(gallery_name, gallery_settings["cover"]["name"])
        cover_image_type = gallery_settings["cover"]["type"]
    else:
        cover_image_path = os.path.join(gallery_path, gallery_settings["cover"])
        cover_image_url = os.path.join(gallery_name, gallery_settings["cover"])
        cover_image_type = "image"

    error(os.path.exists(cover_image_path), "File for %s cover image doesn't exist at "
                                            "%s" % (gallery_name, cover_image_path))

    gallery_cover = {
        "title": gallery_settings["title"],
        "link": gallery_name,
        "sub_title": gallery_settings.get("sub_title", ""),
        "date": gallery_settings.get("date", ""),
        "tags": gallery_settings.get("tags", ""),
        "cover_type": cover_image_type,
        "cover": cover_image_url,
    }
    return gallery_cover


def build_gallery(settings, gallery_settings, gallery_path, template):
    gallery_index_template = template.get_template("gallery-index.html")
    page_template = template.get_template("page.html")

    # this should probably be a factory
    Image.base_dir = os.path.join(os.getcwd(), gallery_path)
    Image.target_dir = os.path.join(os.getcwd(), "build", gallery_path)

    Video.base_dir = os.path.join(os.getcwd(), gallery_path)
    Video.target_dir = os.path.join(os.getcwd(), "build", gallery_path)

    template_to_render = page_template if gallery_settings.get("static") else gallery_index_template

    index_html = open(os.path.join("build", gallery_path, "index.html"), "w")

    index_html.write(template_to_render.render(
        settings=settings,
        gallery=gallery_settings,
        Image=Image,
        Video=Video,
        link=gallery_path
    ).encode("Utf-8"))

    #Build light mode gallery
    if gallery_settings.get("light_mode", False) or (
                settings["settings"].get("light_mode", False) and gallery_settings.get("light_mode") is None):
        # Prepare light mode
        if not os.path.exists(os.path.join("build", gallery_path, "light")):
            os.makedirs(os.path.join("build", gallery_path, "light"))
        gallery_light_path = os.path.join(gallery_path, "light")
        light_templates = get_gallery_templates("light", gallery_light_path)

        Image.base_dir = os.path.join(os.getcwd(), gallery_path)
        Image.target_dir = os.path.join(os.getcwd(), "build", gallery_path)

        Video.base_dir = os.path.join(os.getcwd(), gallery_path)
        Video.target_dir = os.path.join(os.getcwd(), "build", gallery_path)

        light_template_to_render = light_templates.get_template("gallery-index.html")

        index_html = open(os.path.join("build", gallery_light_path, "index.html"), "w")

        index_html.write(light_template_to_render.render(
            settings=settings,
            gallery=gallery_settings,
            Image=Image,
            Video=Video,
            link=gallery_light_path
        ).encode("Utf-8"))



def build_index(settings, galleries_cover, templates, gallery_path=''):
    index_template = templates.get_template("index.html")

    galleries_cover = reversed(sorted(filter(lambda x: x != {}, galleries_cover), key=lambda x: x["date"]))

    # this should probably be a factory
    Image.base_dir = os.path.join(os.getcwd(), gallery_path)
    Image.target_dir = os.path.join(os.getcwd(), "build", gallery_path)

    Video.base_dir = os.path.join(os.getcwd(), gallery_path)
    Video.target_dir = os.path.join(os.getcwd(), "build", gallery_path)

    index_html = open(os.path.join("build", gallery_path, "index.html"), "w")

    index_html.write(index_template.render(
        settings=settings,
        galleries=galleries_cover,
        Image=Image,
        Video=Video
    ).encode("Utf-8"))


def main():
    settings = init()

    front_page_galleries_cover = []

    dirs = filter(lambda x: x not in (".", "..") and os.path.isdir(x) and
                  os.path.exists(os.path.join(os.getcwd(), x, "settings.yaml")), os.listdir(os.getcwd()))

    error(dirs, "I can't find at least one directory with a settings.yaml in the current working "
          "directory (NOT the settings.yaml in your current directory, but one INSIDE A "
          "DIRECTORY in your current working directory), you don't have any gallery?")

    if not os.path.exists("build"):
        os.makedirs("build")

    theme = settings["settings"].get("theme", "exposure")
    templates = get_gallery_templates(theme)
    templates.add_extension('jinja2.ext.with_')
    feed_template = templates.get_template("feed.xml")

    for gallery in dirs:
        front_page_galleries_cover.append(process_directory(gallery, settings, templates))

    if settings["rss"]:
        feed_xml = open(os.path.join("build", "feed.xml"), "w")

        feed_xml.write(feed_template.render(
            settings=settings,
            galleries=reversed(sorted(filter(lambda x: x != {}, front_page_galleries_cover), key=lambda x: x["date"]))
        ).encode("Utf-8"))

    build_index(settings, front_page_galleries_cover, templates)


if __name__ == '__main__':
    main()
