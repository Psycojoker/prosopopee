import sys
import base64

from subprocess import check_output
from path import Path
from email.utils import formatdate
from builtins import str
import ruamel.yaml as yaml
from datetime import datetime

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
    elif not isinstance(gallery_settings, dict):
        error(False, "%s/settings.yaml should be a dict" % folder)
    elif not 'title' in gallery_settings:
        error(False, "You should specify a title in %s/settings.yaml" % folder)

    if gallery_settings.get("date"):
        try:
            datetime.strptime(str(gallery_settings.get("date")), '%Y-%m-%d')
        except ValueError:
            error(False, "Incorrect data format, should be YYYY-MM-DD in %s/settings.yaml" % folder)
    return gallery_settings
