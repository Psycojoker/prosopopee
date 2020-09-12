import logging
import sys
import base64

from subprocess import check_output
from path import Path
from email.utils import formatdate
from builtins import str
import ruamel.yaml as yaml
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    fmt_nok = "%(asctime)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s"
    fmt_ok = "%(asctime)s %(levelname)s - %(message)s"

    FORMATS = {
        logging.INFO: OKGREEN + fmt_ok + ENDC,
        logging.WARNING: WARNING + fmt_nok + ENDC,
        logging.ERROR: FAIL + fmt_nok + ENDC,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def error(test, error_message):
    if test:
        return

    logging.error(error_message)
    sys.exit(1)


def warning(category, warning_message):
    logging.warning("%s: %s", category, warning_message)


def okgreen(category, ok_message):
    logging.info("%s: %s", category, ok_message)


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
        with open(Path(".").joinpath(folder, "settings.yaml").abspath(), "r") as settings:
            gallery_settings = yaml.safe_load(settings.read())
    except (yaml.error.MarkedYAMLError, yaml.YAMLError) as exc:
        msg = "There is something wrong in %s/settings.yaml" % folder
        if isinstance(exc, yaml.error.MarkedYAMLError):
            msg = msg + str(exc.context_mark)
        error(False, msg)
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
