"""
This is the auto update script for going from version 8 to version 9.
"""

import logging

from subprocess import check_call

__version__ = "9"

OONIPROBE_PIP_URL = "ooniprobe==2.3.0"

def _perform_update():
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
