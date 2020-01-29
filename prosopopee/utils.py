import sys
import base64

from subprocess import check_output

from path import Path

from jinja2 import Environment, FileSystemLoader

from email.utils import formatdate
from datetime import datetime

from builtins import str

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
