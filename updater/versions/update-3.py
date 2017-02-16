"""
This is the auto update script for going from version 2 to version 3.
"""

import os
import logging

from subprocess import check_call

__version__ = "3"

OONIPROBE_PIP_URL = "ooniprobe==2.0.0"

FILES_TO_DELETE = [
    '/usr/share/ooni/decks-available/web-full.yaml',
    '/usr/share/ooni/decks-available/web-no-invalid.yaml',
    # Disable the web-full deck
    '/var/lib/ooni/decks-enabled/web-full.yaml'
]

DECKS_TO_ENABLE = [
    'http-invalid.yaml',
    'im.yaml',
    'tor.yaml',
    'web.yaml'
]

def rm_f(path):
    try:
        os.remove(path)
    except OSError:
        pass

def get_disabled_tests():
    try:
        with open('/etc/ooniprobe/disabled-tests') as in_file:
            return map(lambda x: x.strip(), in_file.readlines())
    except EnvironmentError:
        return []

def _perform_update():
    DECKS_AVAILABLE_DIR = "/usr/share/ooni/decks-available"
    DECKS_ENABLED_DIR = "/var/lib/ooni/decks-enabled/"
    for file_path in FILES_TO_DELETE:
        rm_f(file_path)

    disabled_tests = get_disabled_tests()
    if 'http_invalid_request_line' in disabled_tests:
        DECKS_TO_ENABLE.remove('http-invalid.yaml')

    for deck_name in DECKS_TO_ENABLE:
        enabled_path = os.path.join(DECKS_ENABLED_DIR, deck_name)
        if os.path.exists(enabled_path):
            # Skip when the symlink already exists
            continue
        os.symlink(
            os.path.join(DECKS_AVAILABLE_DIR, deck_name),
            enabled_path
        )

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
