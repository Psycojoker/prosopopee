#!/usr/bin/env python

from argparse import ArgumentParser, ArgumentTypeError
import logging
import os
import shutil
import socketserver
import subprocess
import sys
import http.server
import struct

from babel.core import default_locale
from babel.dates import format_date
from multiprocessing import Pool
from PIL import Image, ImageOps, JpegImagePlugin, ImageFile

from path import Path

from jinja2 import Environment, FileSystemLoader

from .cache import CACHE
from .utils import encrypt, rfc822, load_settings, CustomFormatter
from .autogen import autogen
from .__init__ import __version__
from .image import ImageFactory


def loglevel(string):
    try:
        return int(string)
    except ValueError:
        pass
    if hasattr(logging, string):
        return getattr(logging, string)
    raise ArgumentTypeError(
        "takes an integer or a predefined log level from logging module."
    )


parser = ArgumentParser(description="Static site generator for your story.")
parser.add_argument("--version", action="version", version="%(prog)s " + __version__)
parser.add_argument(
    "--log-level",
    default=logging.DEBUG,
    type=loglevel,
    help="Configure the logging level",
)
subparser = parser.add_subparsers(dest="cmd")
parser_build = subparser.add_parser("build", help="Generate static site")
parser_build.add_argument(
    "-j",
    "--jobs",
    default=None,
    type=int,
    help="Specifies number of jobs (thumbnail generations) to run simultaneously. Default: number "
    "of threads available on the system",
)
subparser.add_parser("test", help="Verify all your yaml data")
subparser.add_parser("preview", help="Start preview webserver on port 9000")
subparser.add_parser("deploy", help="Deploy your website")
parser_autogen = subparser.add_parser("autogen", help="Generate gallery automaticaly")
group = parser_autogen.add_mutually_exclusive_group(required=True)
group.add_argument(
    "-d",
    dest="folder",
    metavar="folder",
    help="folder to use for automatic gallery generation",
)
group.add_argument(
    "--all",
    action="store_const",
    const=None,
    dest="folder",
    help="find all folders with settings.yaml for automatic gallery generation",
)
parser_autogen.add_argument(
    "--force",
    action="store_true",
    help="**DESTRUCTIVE** force regeneration of gallery even if sections are already defined.",
)


DEFAULTS = {
    "rss": True,
    "share": False,
    "settings": {},
    "show_date": True,
    "test": False,
    "include": [],
}

SETTINGS = {
    "gm": {
        "quality": 75,
        "auto-orient": True,
        "strip": True,
        "resize": None,
        "progressive": True,
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
        "other": "-qmin 10 -qmax 42 -maxrate 500k -bufsize 1500k",
        "extension": "webm",
    },
    "ffmpeg_audio": {
        "binary": "ffmpeg",
        "loglevel": "error",
        "audio": "libmp3lame",
        "extension": "mp3",
    },
}


ImageFactory.global_options = SETTINGS["gm"]


class Video:
    base_dir = Path()
    target_dir = Path()

    def __init__(self, options):
        if SETTINGS["ffmpeg"] is False:
            logger.error(
                "I couldn't find a binary to convert video and I ask to do so + abort"
            )
            sys.exit(1)

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
        if not options.get("resize"):
            target = target + "." + options["extension"]
        if not CACHE.needs_to_be_generated(source, target, options):
            logger.info("Skipped: %s is already generated", source)
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
            "other": "%s" % options["other"],
        }

        logger.info("Generation: %s", source)

        if options.get("resize"):
            command = (
                "{binary} {loglevel} -i '{source}' {resize} -vframes 1 -y '{target}'"
            )
            command = command.format(**ffmpeg_switches)
        else:
            command = (
                "{binary} {loglevel} -i '{source}' {video} {vbitrate} {other} {audio} "
                "{abitrate} {resolution} {format} -y '{target}'"
            )
            command = command.format(**ffmpeg_switches)

        print(command)

        if os.system(command) != 0:
            logger.error("%s command failed", ffmpeg_switches["binary"])
            sys.exit(1)

        CACHE.cache_picture(source, target, options)

    def copy(self):
        if not DEFAULTS["test"]:
            source, target = (
                self.base_dir.joinpath(self.name),
                self.target_dir.joinpath(self.name),
            )
            options = self.options.copy()
            self.ffmpeg(source, target, options)
        return ""

    def generate_thumbnail(self, gm_geometry):
        thumbnail_name = ".".join(self.name.split(".")[:-1]) + "-%s.jpg" % gm_geometry
        if not DEFAULTS["test"]:
            source, target = (
                self.base_dir.joinpath(self.name),
                self.target_dir.joinpath(thumbnail_name),
            )

            options = self.options.copy()
            options.update({"resize": gm_geometry})

            self.ffmpeg(source, target, options)

        return thumbnail_name

    @property
    def ratio(self):
        if self.options["binary"] == "ffmpeg":
            binary = "ffprobe"
        else:
            binary = "avprobe"
        target = self.base_dir.joinpath(self.name)
        command = (
            binary
            + " -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0"
        )
        command_list = command.split()
        command_list.append(str(target))
        out = subprocess.check_output(command_list)
        width, height = out.decode("utf-8").split(",")
        return float(width) / int(height)

    def __repr__(self):
        return self.name


class Audio:
    base_dir = Path()
    target_dir = Path()

    def __init__(self, options):
        if SETTINGS["ffmpeg"] is False:
            logger.error(
                "I couldn't find a binary to convert audio and I ask to do so + abort"
            )
            sys.exit(1)

        # assuming string
        if not isinstance(options, dict):
            options = {"name": options}
        # used for caching, if it's modified -> regenerate
        self.options = SETTINGS["ffmpeg_audio"].copy()
        self.options.update(options)

    @property
    def name(self):
        return self.options["name"]

    def ffmpeg(self, source, target, options):
        target = target + "." + options["extension"]
        if not CACHE.needs_to_be_generated(source, target, options):
            logger.info("Skipped: %s is already generated", source)
            return

        ffmpeg_switches = {
            "source": source,
            "target": target,
            "binary": "%s" % options["binary"],
            "loglevel": "-loglevel %s" % options["loglevel"],
            "audio": "-c:a %s" % options["audio"],
        }

        logger.info("Generation: %s", source)

        command = "{binary} {loglevel} -i '{source}' {audio} -y '{target}'".format(
            **ffmpeg_switches
        )
        print(command)
        if os.system(command) != 0:
            logger.error("%s command failed", ffmpeg_switches["binary"])
            sys.exit(1)

        CACHE.cache_picture(source, target, options)

    def copy(self):
        if not DEFAULTS["test"]:
            source, target = (
                self.base_dir.joinpath(self.name),
                self.target_dir.joinpath(self.name),
            )
            options = self.options.copy()
            self.ffmpeg(source, target, options)
        return ""

    def __repr__(self):
        return self.name


class TCPServerV4(socketserver.TCPServer):
    allow_reuse_address = True


def get_settings():
    settings = load_settings(".")

    for key, value in list(DEFAULTS.items()):
        if key not in settings:
            settings[key] = value

    for key, value in list(SETTINGS.items()):
        if key not in settings:
            settings[key] = value

    if settings["settings"].get("ffmpeg"):
        SETTINGS["ffmpeg"].update(settings["settings"]["ffmpeg"])

        conv_video = settings["settings"]["ffmpeg"]["binary"]
    else:
        conv_video = "ffmpeg"

    if os.system("which " + conv_video + " > /dev/null") != 0:
        if conv_video == "ffmpeg" and os.system("which avconv > /dev/null") == 0:
            SETTINGS["ffmpeg"]["binary"] = "avconv"
            logger.warning(
                "Video: I couldn't locate ffmpeg but I could find avconv, "
                "switching to avconv for video conversion"
            )
        else:
            logger.warning(
                "Video: I can't locate the %s binary, please install the '%s' package.",
                conv_video,
                conv_video,
            )
            logger.warning(
                "Video: I won't be able to encode video and I will stop if I "
                "encounter a video to convert"
            )
            SETTINGS["ffmpeg"] = False

    if (
        settings["rss"] or settings["share"] or settings["settings"].get("og")
    ) and not settings.get("url"):
        logger.warning(
            "warning: If you want the rss, OpenGraph and/or the social network share to work, "
            "you need to specify the website url in root settings"
        )
        settings["rss"] = False
        settings["share"] = False
        settings["settings"]["og"] = False

    if settings["settings"].get("gm"):
        SETTINGS["gm"].update(settings["settings"]["gm"])

    return settings


def get_local_date_filter(date_locale):
    if date_locale is None:
        date_locale = default_locale("LC_TIME")

    def local_date(value, date_format="dd MMMM yyyy"):
        return format_date(date=value, format=date_format, locale=date_locale)

    return local_date


def get_gallery_templates(
    theme, gallery_path="", parent_templates=None, date_locale=None
):
    theme_path = Path(__file__).parent.joinpath("themes", theme).exists()

    available_themes = theme, "', '".join(
        Path(__file__).parent.joinpath("themes").listdir()
    )

    if not theme_path:
        logger.error(
            "'%s' is not an existing theme + available themes are '%s'",
            theme_path,
            available_themes,
        )
        sys.exit(1)

    templates_dir = [
        Path(".").joinpath("templates").realpath(),
        Path(__file__).parent.joinpath("themes", theme, "templates"),
    ]

    if theme != "exposure":
        templates_dir.append(
            Path(__file__).parent.joinpath("themes", "exposure", "templates")
        )

    subgallery_templates = Environment(
        loader=FileSystemLoader(templates_dir), trim_blocks=True
    )
    subgallery_templates.filters["rfc822"] = rfc822
    subgallery_templates.filters["local_date"] = get_local_date_filter(date_locale)

    Path(".").joinpath("build", gallery_path, "static").rmtree_p()

    if Path(".").joinpath("static").exists():
        shutil.copytree(
            Path(".").joinpath("static"),
            Path(".").joinpath("build", gallery_path, "static"),
        )

    else:
        shutil.copytree(
            Path(__file__).parent.joinpath("themes", theme, "static"),
            Path(".").joinpath("build", gallery_path, "static"),
        )

    return subgallery_templates


def process_directory(
    gallery_name, settings, parent_templates, parent_gallery_path=False
):
    if parent_gallery_path:
        gallery_path = parent_gallery_path.joinpath(gallery_name)
    else:
        gallery_path = gallery_name

    gallery_settings = load_settings(gallery_path)

    gallery_cover = {}

    sub_galleries = [
        x
        for x in Path(".").joinpath(gallery_path).listdir()
        if x.joinpath("settings.yaml").exists()
    ]

    Path("build").joinpath(gallery_path).makedirs_p()

    if not gallery_settings.get("public", True):
        build_gallery(settings, gallery_settings, gallery_path, parent_templates)
        return gallery_cover

    gallery_cover = create_cover(gallery_name, gallery_settings, gallery_path)

    if not sub_galleries:
        build_gallery(settings, gallery_settings, gallery_path, parent_templates)
        return gallery_cover

    if gallery_settings.get("sections", False):
        logger.error(
            "The gallery in %s can't have both sections and subgalleries",
            gallery_name.joinpath("settings.yaml"),
        )
        sys.exit(1)

    # Sub galleries found, create index with them instead of a gallery
    theme = gallery_settings.get("theme", settings.get("theme", "exposure"))

    subgallery_templates = get_gallery_templates(
        theme,
        gallery_path,
        parent_templates,
        date_locale=settings["settings"].get("date_locale"),
    )
    sub_page_galleries_cover = []

    for subgallery in sub_galleries:
        sub_page_galleries_cover.append(
            process_directory(
                subgallery.name, settings, subgallery_templates, gallery_path
            )
        )

    build_index(
        settings,
        sub_page_galleries_cover,
        subgallery_templates,
        gallery_path,
        sub_index=True,
        gallery_settings=gallery_settings,
    )
    gallery_cover["sub_gallery"] = sub_page_galleries_cover

    return gallery_cover


def create_cover(gallery_name, gallery_settings, gallery_path):
    if not gallery_settings.get("cover"):
        logger.error(
            "You should specify a path to a cover picture in %s",
            gallery_name.joinpath("settings.yaml"),
        )
        sys.exit(1)

    if isinstance(gallery_settings["cover"], dict):
        cover_image_path = gallery_path.joinpath(gallery_settings["cover"]["name"])
        cover_image_type = gallery_settings["cover"]["type"]
    else:
        cover_image_path = gallery_path.joinpath(gallery_settings["cover"])
        cover_image_type = "image"

    if not cover_image_path.exists():
        logger.error(
            "File for %s cover image doesn't exist at %s",
            gallery_name,
            cover_image_path,
        )
        sys.exit(1)

    gallery_cover = {
        "title": gallery_settings["title"],
        "link": gallery_path,
        "name": gallery_name + "/",
        "sub_title": gallery_settings.get("sub_title", ""),
        "date": gallery_settings.get("date", ""),
        "tags": gallery_settings.get("tags", ""),
        "cover_type": cover_image_type,
        "cover": gallery_settings["cover"],
    }
    return gallery_cover


def build_gallery(settings, gallery_settings, gallery_path, template):
    gallery_index_template = template.get_template("gallery-index.html")
    page_template = template.get_template("page.html")

    Video.base_dir = Path(".").joinpath(gallery_path)
    Video.target_dir = Path(".").joinpath("build", gallery_path)

    Audio.base_dir = Path(".").joinpath(gallery_path)
    Audio.target_dir = Path(".").joinpath("build", gallery_path)
    if gallery_settings.get("sections"):
        for section in gallery_settings["sections"]:
            if section["type"] not in gallery_settings:
                gallery_settings[section["type"] + "_enabled"] = True

    template_to_render = (
        page_template if gallery_settings.get("static") else gallery_index_template
    )

    html = template_to_render.render(
        settings=settings,
        gallery=gallery_settings,
        Image=ImageFactory,
        Video=Video,
        Audio=Audio,
        link=gallery_path,
        name=gallery_path.split("/", 1)[-1],
    ).encode("Utf-8")

    open(Path("build").joinpath(gallery_path, "index.html"), "wb").write(html)

    if gallery_settings.get("password") or settings.get("password"):
        password = gallery_settings.get("password", settings.get("password"))
        html = encrypt(password, template, gallery_path, settings, gallery_settings)

        open(Path("build").joinpath(gallery_path, "index.html"), "wb").write(html)

    if not gallery_settings.get("light_mode", False) and (
        not settings["settings"].get("light_mode", False)
        or gallery_settings.get("light_mode")
    ):
        return

    # XXX shouldn't this be a call to build_gallery?
    # Build light mode gallery
    # Prepare light mode
    Path("build").joinpath(gallery_path, "light").makedirs_p()
    gallery_light_path = Path(gallery_path).joinpath("light")
    light_templates = get_gallery_templates(
        "light", gallery_light_path, date_locale=settings["settings"].get("date_locale")
    )

    Video.base_dir = Path(".").joinpath(gallery_path)
    Video.target_dir = Path(".").joinpath("build", gallery_path)

    Audio.base_dir = Path(".").joinpath(gallery_path)
    Audio.target_dir = Path(".").joinpath("build", gallery_path)

    light_template_to_render = light_templates.get_template("gallery-index.html")

    html = light_template_to_render.render(
        settings=settings,
        gallery=gallery_settings,
        Image=ImageFactory,
        Video=Video,
        Audio=Audio,
        link=gallery_light_path,
        name=gallery_path.split("/", 1)[-1],
    ).encode("Utf-8")

    open(Path("build").joinpath(gallery_light_path, "index.html"), "wb").write(html)

    if gallery_settings.get("password") or settings.get("password"):
        light_templates.get_template("form.html")
        html = encrypt(
            password, light_templates, gallery_light_path, settings, gallery_settings
        )

        open(Path("build").joinpath(gallery_light_path, "index.html"), "wb").write(html)


def build_index(
    settings,
    galleries_cover,
    templates,
    gallery_path="",
    sub_index=False,
    gallery_settings={},
):
    index_template = templates.get_template("index.html")

    reverse = gallery_settings.get(
        "reverse", settings["settings"].get("reverse", False)
    )
    if reverse:
        galleries_cover = sorted(
            [x for x in galleries_cover if x != {}], key=lambda x: x["date"]
        )
    else:
        galleries_cover = reversed(
            sorted([x for x in galleries_cover if x != {}], key=lambda x: x["date"])
        )

    Video.base_dir = Path(".").joinpath(gallery_path)
    Video.target_dir = Path(".").joinpath("build", gallery_path)

    html = index_template.render(
        settings=settings,
        galleries=galleries_cover,
        sub_index=sub_index,
        Image=ImageFactory,
        Video=Video,
    ).encode("Utf-8")

    open(Path("build").joinpath(gallery_path, "index.html"), "wb").write(html)

    if settings.get("password"):
        password = settings.get("password")
        html = encrypt(password, templates, gallery_path, settings, None)

        open(Path("build").joinpath(gallery_path, "index.html"), "wb").write(html)


def image_params(img, options):
    format = img.format

    params = {"format": format}
    if "progressive" in options:
        params["progressive"] = options["progressive"]
    if "quality" in options:
        params["quality"] = options["quality"]
    if "dpi" in img.info:
        params["dpi"] = img.info["dpi"]
    if format == "JPEG" or format == "MPO":
        params["subsampling"] = JpegImagePlugin.get_sampling(img)

    exif = img.getexif()
    if exif:
        params["exif"] = exif

    return params


def noncached_images(base):
    img = Image.open(base.filepath)
    params = image_params(img, base.options)

    if params.get("exif") and base.options.get("strip", False):
        del params["exif"]

    for thumbnail in base.thumbnails.values():
        filepath = Path("build") / thumbnail.filepath

        if CACHE.needs_to_be_generated(base.filepath, str(filepath), params):
            return base


def render_thumbnails(base):
    logger.debug("(%s) Rendering thumbnails", base.filepath)

    img = Image.open(base.filepath)
    params = image_params(img, base.options)

    exif = params.get("exif")

    # Re-orient if requested and if Orientation EXIF metadata stored in 0x0112 states that
    # it's not upright.
    if exif and base.options.get("auto-orient", False) and exif.get(0x0112, 1) != 1:
        orientation = exif.get(0x0112)

        logger.debug(
            "(%s) Orientation EXIF tag set to %d: rotating thumbnails",
            base.filepath,
            orientation,
        )

        try:
            img = ImageOps.exif_transpose(img)
        except (TypeError, struct.error) as e:
            # Work-around for Pillow < 7.2.0 because of broken handling of some exif metadata
            # Fixed with https://github.com/python-pillow/Pillow/pull/4637
            # Work-around for Pillow < 7.0.0 not handling StripByteCounts being of type long
            # Fixed with https://github.com/python-pillow/Pillow/pull/4626
            method = {
                2: Image.FLIP_LEFT_RIGHT,
                3: Image.ROTATE_180,
                4: Image.FLIP_TOP_BOTTOM,
                5: Image.TRANSPOSE,
                6: Image.ROTATE_270,
                7: Image.TRANSVERSE,
                8: Image.ROTATE_90,
            }.get(orientation)
            img = img.transpose(method)
            if not base.options.get("strip", False):
                logger.warning(
                    "(%s) Original image contains EXIF metadata that Pillow < %s cannot "
                    "handle. Consider upgrading to a newer release. The image will be "
                    "forcefully stripped of its EXIF metadata as a work-around.",
                    base.filepath,
                    "7.2.0" if isinstance(e, TypeError) else "7.0.0",
                )
                del params["exif"]

    if params.get("exif") and base.options.get("strip", False):
        del params["exif"]

    for thumbnail in base.thumbnails.values():
        filepath = Path("build") / thumbnail.filepath

        if not CACHE.needs_to_be_generated(base.filepath, str(filepath), params):
            continue

        # Needed because im.thumbnail replaces the original image
        im = img.copy()

        width, height = thumbnail.size

        if not width or not height:
            # im.thumbnail() needs both valid values in the size tuple.
            # Moreover, the function creates a thumbnail whose dimensions are
            # within the provided size.
            # When only one dimension is specified, the other should thus be
            # outrageously big so that the thumbnail dimension will always be
            # of the specified value.
            IGNORE_DIM = 65596
            height = height if height is not None else IGNORE_DIM
            width = width if width is not None else IGNORE_DIM
            im.thumbnail((width, height), Image.LANCZOS)

        logger.debug(
            "(%s) Creating thumbnail %s: size=%s",
            base.filepath,
            filepath,
            thumbnail.size,
        )
        try:
            im.save(filepath, **params)
        except OSError as e:
            # Work-around for:
            # https://github.com/python-pillow/Pillow/issues/148
            logger.warning(
                '(%s) Failed to save "%s". This usually happens when progressive is set to True and'
                " quality set to a too high value (> 90). Please lower quality or disable"
                ' progressive, globally or for "%s". As a work-around, increase buffer size. This'
                " might result in side-effects.\n"
                'The original error is "%s"',
                base.filepath,
                filepath,
                base.filepath,
                e,
            )
            width, height = (width, height) if width and height else thumbnail.size
            ImageFile.MAXBLOCK = max(
                ImageFile.MAXBLOCK,
                (4 * width * height) + len(im.info.get("icc_profile", "")) + 10,
            )
            im.save(filepath, **params)
        except TypeError as e:
            # Work-around for Pillow < 7.2.0 because of broken handling of some exif metadata
            # Fixed with https://github.com/python-pillow/Pillow/pull/4637
            logger.warning(
                "(%s) Original image contains EXIF metadata that Pillow < 7.2.0 cannot handle. "
                "Consider upgrading to a newer release. The image will be forcefully stripped of "
                "its EXIF metadata as a work-around.\n"
                'The original error is "%s"',
                base.filepath,
                e,
            )
            del params["exif"]
            im.save(filepath, **params)

        logger.debug(
            "(%s) Done creating thumbnail %s: size=%s",
            base.filepath,
            filepath,
            thumbnail.size,
        )
        CACHE.cache_picture(base.filepath, str(filepath), params)


logger = logging.getLogger("prosopopee")


def main():
    args = parser.parse_args()

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)
    logger.setLevel(args.log_level)

    settings = get_settings()

    front_page_galleries_cover = []

    galleries_dirs = [
        x for x in Path(".").listdir() if x.joinpath("settings.yaml").exists()
    ]
    includes = [x for x in settings["include"] if Path(".").joinpath(x).exists()]

    if not galleries_dirs:
        logger.error(
            "I can't find at least one directory with a settings.yaml in the current "
            "working directory (NOT the settings.yaml in your current directory, but one "
            "INSIDE A DIRECTORY in your current directory), you don't have any gallery?"
        )
        sys.exit(1)

    if args.cmd == "test":
        DEFAULTS["test"] = True

    if args.cmd == "preview":
        if not Path("build").exists():
            logger.error("Please build the website before launch preview")
            sys.exit(1)

        os.chdir("build")
        handler = http.server.SimpleHTTPRequestHandler
        httpd = TCPServerV4(("", 9000), handler)
        print("Start server on http://localhost:9000")
        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            print("\nShutdown server")
            httpd.shutdown()
            raise

    if args.cmd == "deploy":
        if os.system("which rsync > /dev/null") != 0:
            logger.error(
                "I can't locate the rsync + please install the 'rsync' package."
            )
            sys.exit(1)
        if not Path("build").exists():
            logger.error("Please build the website before launch deployment")
            sys.exit(1)

        r_dest = settings["settings"]["deploy"]["dest"]
        if settings["settings"]["deploy"]["others"]:
            r_others = settings["settings"]["deploy"]["others"]
        else:
            r_others = ""
        if settings["settings"]["deploy"]["ssh"]:
            r_username = settings["settings"]["deploy"]["username"]
            r_hostname = settings["settings"]["deploy"]["hostname"]
            r_cmd = "rsync -avz --progress %s build/* %s@%s:%s" % (
                r_others,
                r_username,
                r_hostname,
                r_dest,
            )
        else:
            r_cmd = "rsync -avz --progress %s build/* %s" % (r_others, r_dest)
        if os.system(r_cmd) != 0:
            logger.error("deployment failed")
            sys.exit(1)
        return

    if args.cmd == "autogen":
        autogen(args.folder, args.force)
        return

    Path("build").makedirs_p()
    theme = settings["settings"].get("theme", "exposure")
    date_locale = settings["settings"].get("date_locale")
    templates = get_gallery_templates(theme, date_locale=date_locale)
    templates.add_extension("jinja2.ext.with_")

    if Path("custom.js").exists():
        shutil.copy(Path("custom.js"), Path(".").joinpath("build", "", "static", "js"))
        settings["custom_js"] = True

    if Path("custom.css").exists():
        shutil.copy(
            Path("custom.css"), Path(".").joinpath("build", "", "static", "css")
        )
        settings["custom_css"] = True

    logger.info("Building galleries...")

    for gallery in galleries_dirs:
        front_page_galleries_cover.append(
            process_directory(gallery.normpath(), settings, templates)
        )

    for i in includes:
        srcdir = Path(i).dirname()
        dstdir = Path(".").joinpath("build", srcdir)
        if srcdir != "":
            os.makedirs(dstdir, exist_ok=True)
        d = shutil.copy2(i, dstdir)
        logger.warning("copied", d)

    if settings["rss"]:
        feed_template = templates.get_template("feed.xml")

        xml = feed_template.render(
            settings=settings,
            galleries=reversed(
                sorted(
                    [x for x in front_page_galleries_cover if x != {}],
                    key=lambda x: x["date"],
                )
            ),
        ).encode("Utf-8")

        open(Path("build").joinpath("feed.xml"), "wb").write(xml)

    build_index(settings, front_page_galleries_cover, templates)

    if DEFAULTS["test"] is True:
        logger.info("Success: HTML file building without error")
        sys.exit(0)

    # If prosopopee is started without any argument, 'build' is assumed but the jobs parameter
    # is not part of the namespace, so set its default to None (or 'number of available CPU
    # treads')
    jobs = args.jobs if args.cmd else None

    with Pool(jobs) as pool:
        # Pool splits the iterable into pre-defined chunks which are then assigned to processes.
        # There is no other scheduling in play after that. This is an issue when chunks are
        # outrageously unbalanced in terms of CPU time which happens when most galleries are
        # already built and thus hit the cache but not some, in which case, only a few processes
        # will run and not the full CPU power will be used, wasting time.
        # In order to optimize this, a first very quick run through the list of images is done
        # to list only those which actually need to be generated.
        # In the following implementation, the first pool.map function will be slightly
        # unbalanced because some images will hit the cache directly while some won't at all,
        # iterating over all the thumbnails it needs to create. But it is **much** less
        # unbalanced than sending to render_thumbnails all images even those which would hit the
        # cache. After the first pool.map, the second will only contain images with at least one
        # thumbnail to create.
        logger.info("Generating list of thumbnails to create...")
        base_imgs = pool.map(noncached_images, ImageFactory.base_imgs.values())
        base_imgs = [img for img in base_imgs if img]
        if base_imgs:
            logger.info("Generating thumbnails...")
            pool.map(render_thumbnails, base_imgs)

    CACHE.cache_dump()


if __name__ == "__main__":
    main()
