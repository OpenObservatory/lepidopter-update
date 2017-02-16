"""
This is the auto update script for going from version 5 to version 6.
"""

import logging

from subprocess import check_call

__version__ = "6"

OONIPROBE_PIP_URL = "ooniprobe==2.1.0"
def _perform_update():
    # Fix pip bug introduced in setuptools v34.0.0
    # http://setuptools.readthedocs.io/en/latest/history.html#v34-0-0
    check_call(["apt-get", "-q", "update"])
    check_call(["apt-get", "-y", "install", "-t", "stretch", "python-pip"])
    # Remove previously installed python packages
    check_call(["apt-get", "-y", "autoremove"])
    check_call(["pip", "install", "--upgrade", "setuptools"])

    check_call(["pip", "install", "--upgrade", OONIPROBE_PIP_URL])

def run():
    try:
        check_call(["systemctl", "stop", "ooniprobe"])
    except Exception as exc:
        logging.error("Failed to stop ooniprobe-agent")
        logging.exception(exc)
    try:
        _perform_update()
    except Exception as exc:
        logging.exception(exc)
        raise
    finally:
        try:
            check_call(["systemctl", "start", "ooniprobe"])
        except Exception as exc:
            logging.error("Failed to start ooniprobe-agent")
            logging.exception(exc)

if __name__ == "__main__":
    run()
