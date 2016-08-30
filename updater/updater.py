#!/usr/bin/env python2

import os
import re

# XPY3 this is deprecated in python3
import imp
import time
import shutil
import logging
import tempfile
import argparse

from subprocess import check_output, check_call, CalledProcessError

# UPDATE_BASE_URL/latest/version must return an integer containing the latest version number
# UPDATE_BASE_URL/VERSION/update.py must return the update script for VERSION
# UPDATE_BASE_URL/VERSION/update.py.asc must return a valid GPG signature for update.py
UPDATE_BASE_URL = "https://github.com/OpenObservatory/lepidopter-update/releases/download/"

CURRENT_VERSION_PATH = "/etc/lepidopter/current_version"
UPDATER_PATH = "/opt/ooni/updater/versions/"
PUBLIC_KEY_PATH = "/opt/ooni/updater/public.asc"

class RequestFailed(Exception):
    pass

def get_request(url, follow_redirects=True):
    cmd = ["curl", "-q"]
    if follow_redirects is True:
        cmd.append("-L")
    cmd.append(url)

    tmp_file = tempfile.TemporaryFile()

    try:
        check_call(cmd, stdout=tmp_file)
    except CalledProcessError:
        raise RequestFailed

    tmp_file.seek(0)

    return tmp_file.read()

def get_current_version():
    if not os.path.exists(CURRENT_VERSION_PATH):
        return 0
    with open(CURRENT_VERSION_PATH) as in_file:
        version = in_file.read()
    return int(version)

def get_latest_version():
    version = get_request(UPDATE_BASE_URL + "latest/version")
    return int(version)

class InvalidSignature(Exception):
    pass

class InvalidPublicKey(Exception):
    pass


def verify_file(signature_path, signer_pk_path):
    tmp_dir = tempfile.mkdtemp()
    tmp_key = os.path.join(tmp_dir, "signing-key.gpg")

    try:
        try:
            check_call(["gpg", "--batch", "--yes", "-o", tmp_key,
                        "--dearmor", signer_pk_path])
        except CalledProcessError:
            raise InvalidPublicKey

        try:
            output = check_output(["gpg", "--batch", "--status-fd", "1",
                                   "--no-default-keyring", "--keyring",
                                   tmp_key, "--trust-model", "always",
                                   "--verify", signature_path])
        except CalledProcessError:
            raise InvalidSignature

    except Exception as e:
        raise e

    finally:
        shutil.rmtree(tmp_dir)

    return output

class UpdateFailed(Exception):
    pass

def perform_update(version):
    try:
        updater = get_request(UPDATE_BASE_URL + "{0}/update.py".format(version))
        updater_path = os.path.join(UPDATER_PATH, "update-{0}.py".format(version))
    except RequestFailed:
        logging.error("Failed to download update file")
        raise UpdateFailed

    try:
        updater_sig = get_request(UPDATE_BASE_URL + "{0}/update.py.asc".format(version))
        updater_sig_path = os.path.join(UPDATER_PATH, "update-{0}.py.asc".format(version))
    except RequestFailed:
        logging.error("Failed to download update file")
        raise UpdateFailed

    with open(updater_path, "w+") as out_file:
        out_file.write(updater)
    with open(updater_sig_path, "w+") as out_file:
        out_file.write(updater_sig)

    try:
        verify_file(updater_sig_path, PUBLIC_KEY_PATH)
    except InvalidSignature:
        logging.error("Found an invalid signature. Bailing")
        raise UpdateFailed

    updater = imp.load_source('updater_{0}'.format(version),
                              updater_path)

    try:
        logging.info("Running install script")
        updater.run()
    except Exception:
        logging.error("Failed to run the version update script for version {0}".format(version))
        raise UpdateFailed

    # Update the current version number
    with open(CURRENT_VERSION_PATH, "w+") as out_file:
        out_file.write(str(version))

def update_to_version(from_version, to_version):
    versions = range(from_version + 1, to_version + 1)
    for version in versions:
        try:
            perform_update(version)
        except UpdateFailed:
            logging.error("Failed to update to version {0}".format(version))
            return

def check_for_update():
    logging.info("Checking for update")
    current_version = get_current_version()
    try:
        latest_version = get_latest_version()
    except RequestFailed:
        logging.error("Failed to learn the latest version")
        return

    if current_version < latest_version:
        logging.info("Updating {0}->{1}".format(current_version, latest_version))
        update_to_version(current_version, latest_version)
    else:
        logging.info("Already up to date")

class InvalidInterval(Exception):
    pass

def _get_interval(interval):
    """
    Returns the interval in seconds.
    """
    seconds = 0
    INTERVAL_REGEXP = re.compile("(\d+d)?(\d+h)?(\d+m)?")
    m = INTERVAL_REGEXP.match(interval)
    days, hours, minutes = m.groups()

    if days is not None:
        seconds += int(days[:-1]) * 24 * 60 * 60
    if hours is not None:
        seconds += int(hours[:-1]) * 60 * 60
    if minutes is not None:
        seconds += int(minutes[:-1]) * 60

    if seconds == 0:
        try:
            seconds = int(interval)
        except ValueError:
            raise InvalidInterval
    return seconds

def update(args):
    print args
    if args.watch is True:
        seconds = _get_interval(args.interval)
        while True:
            check_for_update()
            time.sleep(seconds)
    else:
        check_for_update()

class InvalidLogLevel(Exception):
    pass

def _setup_logging(args):
    log_file = args.log_file

    try:
        log_level = getattr(logging, args.log_level)
    except AttributeError:
        raise InvalidLogLevel()

    logging.basicConfig(filename=log_file, level=log_level)

def main():
    parser = argparse.ArgumentParser(description="Auto-update system for lepidopter")
    parser.add_argument('--log-file', help="Specify the path to the logfile")
    parser.add_argument('--log-level', help="Specify the loglevel (CRITICAL, ERROR, WARNING, INFO, DEBUG)", default="INFO")

    sub_parsers = parser.add_subparsers()

    parser_update = sub_parsers.add_parser('update')
    parser_update.add_argument('--watch',
                               action='store_true',
                               help="Keep watching for changes in version and automatically update when a new version is available")
    parser_update.add_argument('--interval', default='6h')
    parser_update.set_defaults(func=update)

    args = parser.parse_args()
    _setup_logging(args)
    args.func(args)


if __name__ == "__main__":
    main()
