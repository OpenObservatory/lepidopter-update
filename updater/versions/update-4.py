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

    check_call(["pip", "install", "--upgrade", OONIPROBE_PIP_URL])

def run():
    check_call(["systemctl", "stop", "ooniprobe"])
    try:
        _perform_update()
    except Exception as exc:
        logging.exception(exc)
        raise
    finally:
        check_call(["systemctl", "start", "ooniprobe"])

if __name__ == "__main__":
    run()
