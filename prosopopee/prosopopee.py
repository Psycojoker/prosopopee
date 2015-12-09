#!/usr/bin/env python

import os
import sys
import yaml
import shutil

from jinja2 import Environment, FileSystemLoader

templates = Environment(loader=FileSystemLoader([os.path.realpath(os.path.join(os.getcwd(), "templates")), os.path.join(os.path.split(os.path.realpath(__file__))[0], "templates")]))
index_template = templates.get_template("index.html")
gallery_index_template = templates.get_template("gallery-index.html")


class TemplateFunctions():
    def __init__(self, base_dir, target_dir, has_gm):
        self.base_dir = base_dir
        self.target_dir = target_dir

    def copy_image(self, image):
        shutil.copyfile(os.path.join(self.base_dir, image), os.path.join(self.target_dir, image))
        print os.path.join(self.base_dir, image), "->", os.path.join(self.target_dir, image)
        return ""

    def generate_thumbnail(self, image, gm_geometry):
        thumbnail_name = image.split(".")
        thumbnail_name[-2] += "-small"
        thumbnail_name = ".".join(thumbnail_name)

        command = "gm convert %s -resize %s %s" % (os.path.join(self.base_dir, image), gm_geometry, os.path.join(self.target_dir, thumbnail_name))
        print command
        os.system(command)
        return thumbnail_name


def error(test, error_message):
    if test:
        return

    sys.stderr.write(error_message)
    sys.stderr.write("\n")
    sys.stderr.write("Abort.\n")
    sys.exit(1)


def main():
    has_gm = True
    if os.system("which gm > /dev/null") != 0:
        has_gm = False
        sys.stderr.write("WARNING: I can't locate the 'gm' binary, I won't be able to resize images.\n")

    error(os.path.exists(os.path.join(os.getcwd(), "settings.yaml")), "I can't find a settings.yaml in the current working directory")

    settings = yaml.safe_load(open("settings.yaml", "r"))

    error(isinstance(settings, dict), "Your settings.yaml should be a dict")
    error(settings.get("title"), "You should specify a title in your main settings.yaml")

    front_page_galleries_cover = []

    dirs = filter(lambda x: x not in (".", "..") and os.path.isdir(x) and os.path.exists(os.path.join(os.getcwd(), x, "settings.yaml")), os.listdir(os.getcwd()))

    error(dirs, "I can't find at least one directory with a settings.yaml in the current working directory, you don't have any gallery?")

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

        front_page_galleries_cover.append({
            "title": gallery_title,
            "link": gallery,
            "sub_title": gallery_sub_title,
            "date": gallery_date,
            "cover": cover_image_path,
        })

        if not os.path.exists(os.path.join("build", gallery)):
            os.makedirs(os.path.join("build", gallery))

        open(os.path.join("build", gallery, "index.html"), "w").write(gallery_index_template.render(settings=settings, gallery=gallery_settings, helpers=TemplateFunctions(os.path.join(os.getcwd(), gallery), os.path.join(os.getcwd(), "build", gallery), has_gm=has_gm)).encode("Utf-8"))

    front_page_galleries_cover = sorted(front_page_galleries_cover, key=lambda x: x["date"])

    open(os.path.join("build", "index.html"), "w").write(index_template.render(settings=settings, galleries=front_page_galleries_cover, helpers=TemplateFunctions(os.getcwd(), os.path.join(os.getcwd(), "build"), has_gm=has_gm)).encode("Utf-8"))


if __name__ == '__main__':
    main()
