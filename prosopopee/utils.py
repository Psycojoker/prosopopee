import sys


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
