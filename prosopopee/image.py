import imagesize
import logging
import re
import sys

from json import dumps as json_dumps
from pathlib import Path
from zlib import crc32

from .utils import remove_superficial_options


logger = logging.getLogger("prosopopee." + __name__)


class ImageCommon:
    @property
    def ratio(self):
        # For when BaseImage.ratio is called before BaseImage.copy() is.
        if not self.size:
            self.size = imagesize.get(self.filepath)
        width, height = self.size
        return width / height


class Thumbnail(ImageCommon):
    def __init__(self, base_filepath, base_id, size):
        self.filepath = self.__filepath(base_filepath, base_id, size)
        self.size = size

    def __filepath(self, base_filepath, base_id, size):
        p = Path(base_filepath)
        width, height = size
        suffix = "-{base_id}-{width}x{height}{suffix}".format(
            base_id=base_id,
            width=width if width else "",
            height=height if height else "",
            suffix=p.suffix,
        )

        return p.parent / (p.stem + suffix)


class BaseImage(ImageCommon):
    re_rsz = re.compile(r"^(\d+)%$")

    def __init__(self, options, global_options):
        self.copysize = None
        self.thumbnails = dict()
        self.options = global_options.copy()
        self.options.update(options)
        self.filepath = self.options["name"]
        self.resize = self.options.get("resize")
        self.options = remove_superficial_options(self.options)
        self.chksum_opt = crc32(
            bytes(json_dumps(self.options, sort_keys=True), "utf-8")
        )

    def copy(self):
        if not self.copysize:
            width, height = imagesize.get(self.filepath)

            if self.resize:
                match = BaseImage.re_rsz.match(str(self.resize))
                if not match:
                    logger.error(
                        "(%s) specified resize setting is not a percentage",
                        self.filepath,
                    )
                    sys.exit(1)
                percentage = int(match.group(1))
                width, height = width * percentage // 100, height * percentage // 100

            self.copysize = width, height

        return self.thumbnail(self.copysize)

    def thumbnail(self, size):
        thumbnail = Thumbnail(self.filepath, self.chksum_opt, size)
        return self.thumbnails.setdefault(thumbnail.filepath, thumbnail).filepath.name


# TODO: add support for looking into parent directories (name: ../other_gallery/pic.jpg)
class ImageFactory:
    base_imgs = dict()
    global_options = dict()

    @classmethod
    def get(cls, path, image):
        if not isinstance(image, dict):
            image = {"name": image}

        if "name" not in image:
            logger.error(
                'At least one image in "%s" does not have a `name` property, please add the '
                "filename of the image to a `name` property.",
                path + "/settings.yaml",
            )
            sys.exit(1)

        im = image.copy()
        # To resolve paths with .. in them, we need to resolve the path first and then
        # find the relative path to the source (current) directory.
        im["name"] = Path(path).joinpath(im["name"]).resolve().relative_to(Path.cwd())
        img = BaseImage(im, cls.global_options)
        return cls.base_imgs.setdefault(img.filepath / str(img.chksum_opt), img)
