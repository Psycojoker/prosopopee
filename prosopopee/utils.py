import logging
import sys
import base64
from subprocess import check_output
from email.utils import formatdate
from datetime import datetime
from builtins import str

from path import Path
import ruamel.yaml as yaml


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
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


def makeform(template, settings, gallery_settings):
    from_template = template.get_template("form.html")
    form = base64.b64encode(
        from_template.render(settings=settings, gallery=gallery_settings).encode(
            "Utf-8"
        )
    )
    return str(form, "utf-8")


def encrypt(password, template, gallery_path, settings, gallery_settings):
    encrypted_template = template.get_template("encrypted.html")
    index_plain = Path("build").joinpath(gallery_path, "index.html")
    encrypted = check_output(
        'cat %s | openssl enc -e -base64 -A -aes-256-cbc -md md5 -pass pass:"%s"'
        % (index_plain, password),
        shell=True,
    )
    html = encrypted_template.render(
        settings=settings,
        form=makeform(template, settings, gallery_settings),
        ciphertext=str(encrypted, "utf-8"),
        gallery=gallery_settings,
    ).encode("Utf-8")
    return html


def rfc822(date):
    epoch = datetime.utcfromtimestamp(0).date()
    return formatdate((date - epoch).total_seconds())


def load_settings(folder):
    try:
        with open(
            Path(".").joinpath(folder, "settings.yaml").abspath(), "r"
        ) as settings:
            gallery_settings = yaml.safe_load(settings.read())
    except (yaml.error.MarkedYAMLError, yaml.YAMLError) as exc:
        msg = "There is something wrong in %s/settings.yaml" % folder
        if isinstance(exc, yaml.error.MarkedYAMLError):
            msg = msg + str(exc.context_mark)
        logging.error(msg)
        sys.exit(1)
    except ValueError:
        logging.error(
            "Incorrect data format, should be YYYY-MM-DD in %s/settings.yaml", folder
        )
        sys.exit(1)
    except Exception as exc:
        logging.exception(exc)
        sys.exit(1)

    if gallery_settings is None:
        logging.error("The %s/settings.yaml file is empty", folder)
        sys.exit(1)
    elif not isinstance(gallery_settings, dict):
        logging.error("%s/settings.yaml should be a dict", folder)
        sys.exit(1)
    elif "title" not in gallery_settings:
        logging.error("You should specify a title in %s/settings.yaml", folder)
        sys.exit(1)

    if gallery_settings.get("date"):
        try:
            datetime.strptime(str(gallery_settings.get("date")), "%Y-%m-%d")
        except ValueError:
            logging.error(
                "Incorrect data format, should be YYYY-MM-DD in %s/settings.yaml",
                folder,
            )
            sys.exit(1)
    return gallery_settings
