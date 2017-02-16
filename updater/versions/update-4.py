"""
This is the auto update script for going from version 3 to version 4.
"""

import os
import logging

from datetime import datetime, timedelta

from subprocess import check_call

__version__ = "4"

OONIPROBE_PIP_URL = "ooniprobe==2.0.1"
OONI_LOG_PATH = "/var/log/ooni/"

past_2_days_ts = int((datetime.now() - timedelta(days=2)).strftime("%s"))

def _perform_update():
    # Deletes log files that are older than 2 days.
    # This is due to a problem in ooniprobe with logfiles ending up being too
    # large.
    for filename in os.listdir(OONI_LOG_PATH):
        filepath = os.path.join(OONI_LOG_PATH, filename)
        if os.path.getmtime(filepath) < past_2_days_ts:
            logging.info("Deleting %s" % filepath)
            os.unlink(filepath)

    # Fix pip bug introduced in setuptools v34.0.0
    # http://setuptools.readthedocs.io/en/latest/history.html#v34-0-0
    check_call(["apt-get", "-q", "update"])
    check_call(["apt-get", "-y", "install", "-t", "stretch", "python-pip"])
    # Remove previously installed python packages
    check_call(["apt-get", "-y", "autoremove"])
    check_call(["pip", "install", "setuptools==34.2.0"])

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
