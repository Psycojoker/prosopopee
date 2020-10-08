import sys
import base64
import json
import piexif
import urllib.request, urllib.error, urllib.parse
import ruamel.yaml as yaml

from importlib_metadata import version
from subprocess import check_output
from path import Path
from email.utils import formatdate
from builtins import str
from datetime import datetime
from PIL import Image


class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def error(test, error_message):
    if test:
        return

    sys.stderr.write(bcolors.FAIL + "Abort: " + bcolors.ENDC + error_message)
    sys.stderr.write("\n")
    sys.exit(1)


def warning(logging, warning_message):
    sys.stderr.write("%s%s: %s%s" % (bcolors.WARNING, logging, bcolors.ENDC, warning_message))
    sys.stderr.write("\n")


def okgreen(logging, ok_message):
    sys.stderr.write("%s%s: %s%s" % (bcolors.OKGREEN, logging, bcolors.ENDC, ok_message))
    sys.stderr.write("\n")


def makeform(template, settings, gallery_settings):
    from_template = template.get_template("form.html")
    form = base64.b64encode(from_template.render(settings=settings, gallery=gallery_settings).encode("Utf-8"))
    return str(form, 'utf-8')


def encrypt(password, template, gallery_path, settings, gallery_settings):
    encrypted_template = template.get_template("encrypted.html")
    index_plain = Path("build").joinpath(gallery_path, "index.html")
    encrypted = check_output('cat %s | openssl enc -e -base64 -A -aes-256-cbc -md md5 -pass pass:"%s"' % (index_plain, password), shell=True)
    html = encrypted_template.render(
        settings=settings,
        form=makeform(template, settings, gallery_settings),
        ciphertext=str(encrypted, 'utf-8'),
        gallery=gallery_settings,
    ).encode("Utf-8")
    return html


def rfc822(dt):
    epoch = datetime.utcfromtimestamp(0).date()
    return formatdate((dt - epoch).total_seconds())


def load_settings(folder):
    try:
        gallery_settings = yaml.safe_load(open(Path(".").joinpath(folder, "settings.yaml").abspath(), "r"))
    except yaml.YAMLError as exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            error(False, "There are something wrong in %s/settings.yaml line %s" % (folder, mark.line))
        else:
            error(False, "There are something wrong in %s/settings.yaml" % folder)
    except ValueError:
        error(False, "Incorrect data format, should be YYYY-MM-DD in %s/settings.yaml" % folder)
    if gallery_settings is None:
        error(False, "The %s/settings.yaml file is empty" % folder)
    else:
        if gallery_settings.get("date"):
            try:
                datetime.strptime(str(gallery_settings.get("date")), '%Y-%m-%d')
            except ValueError:
                error(False, "Incorrect data format, should be YYYY-MM-DD in %s/settings.yaml" % folder)
        return gallery_settings


def check_version():
    installed_version = version("prosopopee")
    url = "https://pypi.python.org/pypi/prosopopee/json"
    try:
        data = json.load(urllib.request.urlopen(urllib.request.Request(url)))
    except:
        return
    versions = list(data["releases"].keys())
    latest_version = (versions[-1])
    if installed_version < latest_version:
        warning("Update", "The version %s of Prosopopee is available, Think to update it" % latest_version)


def rotate_jpeg(filename):
    img = Image.open(filename)
    if "exif" in img.info:
        try:
            exif_dict = piexif.load(img.info["exif"])
        except:
            return

        if piexif.ImageIFD.Orientation in exif_dict["0th"]:
            orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
            try:
                exif_bytes = piexif.dump(exif_dict)
            except:
                return

            if orientation == 2:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                img = img.rotate(180)
            elif orientation == 4:
                img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 5:
                img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 7:
                img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

            img.save(filename, exif=exif_bytes)
