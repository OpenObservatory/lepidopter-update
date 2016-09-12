"""
This is the updater from version Y to X.
"""
import os
import shutil
import logging

from subprocess import check_call

# XXX remember to set the version correctly
__version__ = "X"

def _perform_update():
    # XXX put in here the logic for the update
    pass

def run():
    check_call(["systemctl", "stop", "ooniprobe"])
    try:
        _perform_update()
    except Exception as exc:
        logging.exception(exc)
    finally:
        check_call(["systemctl", "start", "ooniprobe"])

if __name__ == "__main__":
    run()
