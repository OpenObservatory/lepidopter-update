"""
This is the auto update script for going from version 5 to version 6.
"""

import logging

from subprocess import check_call

__version__ = "6"

OONIPROBE_PIP_URL = "ooniprobe==2.1.0"
def _perform_update():
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
