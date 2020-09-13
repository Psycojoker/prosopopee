import logging
import os
import sys
from time import gmtime, strftime
from glob import glob
from jinja2 import Template
from path import Path
from .utils import load_settings
from PIL import Image
from PIL.ExifTags import TAGS

data = '''title: {{ title }}
date: {{ date }}
cover: {{ cover }}
sections:
  - type: pictures-group
    images:
      -
{% set nb = namespace(value=range(2,5)|random) %}
{% set count = namespace(value=0) %}
{% for file in files %}
{% if count.value != nb.value %}
{% set file = file.split('/') %}
         - {{ file[-1] }}
{% set count.value = count.value + 1 %}
{% else %}
{% if not loop.last %}
      -
{% endif %}
{% set count.value = 0 %}
{% set nb. value = range(2,5)|random %}
{% endif %}
{% endfor %}
'''

types = ('*.JPG', '*.jpg', '*.JPEG', '*.jpeg', '*.png', '*.PNG')


def get_exif(filename):
    exif = Image.open(filename)._getexif()
    if exif is not None:
        for tag in exif:
            decoded = TAGS.get(tag, tag)
            if decoded == 'DateTime':
                return exif[tag]

    return strftime("%Y:%m:%d %H:%M:00", gmtime(os.path.getmtime(filename)))


def build_template(folder, force):
    files_grabbed = []

    gallery_settings = load_settings(folder)

    if 'static' in gallery_settings:
        logging.info("Skipped: Nothing to do in %s gallery", folder)
        return

    if any(req not in gallery_settings for req in ['title', 'date', 'cover']):
        logging.error("You need configure first, the title, date and cover in %s/settings.yaml "
                "to use autogen", folder)
        sys.exit(1)

    if 'sections' in gallery_settings and force is not True:
        logging.info("Skipped: %s gallery is already generated", folder)
        return

    for files in types:
        files_grabbed.extend(glob(Path(".").joinpath(folder, files)))
    tm = Template(data, trim_blocks=True)
    msg = tm.render(title=gallery_settings['title'],
                    date=gallery_settings['date'],
                    cover=gallery_settings['cover'],
                    files=sorted(files_grabbed, key=get_exif)
                    )
    f = open(Path(".").joinpath(folder, "settings.yaml").abspath(), "w")
    f.write(msg)
    logging.info("Generation: %s gallery", folder)


def autogen(folder=None, force=False):
    if folder:
        build_template(folder, force)
        return

    for x in glob("./*/**/settings.yaml", recursive=True):
        folder = x.rsplit('/', 1)[0]
        if not glob(folder + "/**/settings.yaml"):
            build_template(folder, force)
