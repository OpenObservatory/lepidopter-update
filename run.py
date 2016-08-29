import os
import shutil
import argparse
from subprocess import call

from datetime import datetime

import git
import requests

CWD = os.path.dirname(__file__)

try:
    GITHUB_TOKEN = open("GITHUB_TOKEN").read().strip()
except Exception:
    print("You must write your github token to a file called \"GITHUB_TOKEN\"")
    raise

GH_BASE_URL = "https://api.github.com/repos/OpenObservatory/lepidopter-update"
GPG_KEY_ID = "204F9D29"

def _get_latest_release_tag():
    params = {
        "access_token": GITHUB_TOKEN
    }
    r = requests.get(GH_BASE_URL + "/releases/latest",
                    params=params)
    return r.json()['tag_name']


def _create_latest_version():
    params = {
        "access_token": GITHUB_TOKEN
    }
    data = {
        "tag_name": "latest",
        "target_commitish": "master",
        "name": "latest",
        "body": "This tag is used to obtain the latest version",
        "draft": False,
        "prerelease": True
    }
    r = requests.post(GH_BASE_URL + "/releases",
                      params=params, json=data)
    try:
        assert r.status_code == 201
    except:
        print r.text
        raise
    return r.json()["id"]

def _upload_asset(upload_url, name, content_type, data):
    headers = {
        "Content-Type": content_type
    }
    params = {
        "access_token": GITHUB_TOKEN,
        "name": name
    }
    print("Uploading asset {0}".format(params["name"]))
    print("to: {0}".format(upload_url))
    r = requests.post(upload_url,
                      params=params,
                      headers=headers,
                      data=data)
    if r.status_code != 201:
        raise Exception("Could not upload asset")
    return r.json()

def _delete_all_assets(release_id):
    params = {
        "access_token": GITHUB_TOKEN,
    }
    r = requests.get(GH_BASE_URL + "/releases/{0}/assets".format(release_id),
                     params=params)
    for asset in r.json():
        requests.delete(GH_BASE_URL + "/releases/assets/{0}".format(asset["id"]),
                        params=params)
        assert r.status_code/100 == 2

def update_latest_version(tag_name):
    params = {
        "access_token": GITHUB_TOKEN
    }
    r = requests.get(GH_BASE_URL + "/releases/tags/latest",
                     params=params)
    if r.status_code == 404:
        release_id = _create_latest_version()
    elif r.status_code == 200:
        release_id = r.json()["id"]

    data = {
        "target_commitish": "master"
    }
    r = requests.patch(GH_BASE_URL + "/releases/{0}".format(release_id),
                       params=params, json=data)
    assert r.status_code == 200

    upload_url = r.json()['upload_url'].replace("{?name,label}", "")
    _delete_all_assets(release_id)
    _upload_asset(upload_url, "version", "text/plain", tag_name)

def create_new_release(version):
    params = {
        "access_token": GITHUB_TOKEN
    }
    data = {
        "tag_name": str(version),
        "target_commitish": "master",
        "name": str(version),
        "body": "Update for lepidopter {0}".format(
            datetime.now().strftime("%Y-%m-%d")
        ),
        "draft": False,
        "prerelease": False
    }
    r = requests.post(GH_BASE_URL + "/releases",
                      params=params, json=data)
    try:
        assert r.status_code == 201
    except:
        print r.text
        return
    j = r.json()
    upload_url = j["upload_url"].replace("{?name,label}", "")
    update_file = "updater/versions/update-{0}.py".format(version)
    update_file_sig = "updater/versions/update-{0}.py.asc".format(version)
    content_type = "text/plain"

    data = open(update_file, "r").read()
    _upload_asset(upload_url,
                  name="update.py",
                  content_type=content_type,
                  data=data)

    data = open(update_file_sig, "r").read()
    _upload_asset(upload_url,
                  name="update.py.asc",
                  content_type=content_type,
                  data=data)

    update_latest_version(str(version))

def get_next_version():
    with open(os.path.join(CWD, "updater", "latest_version")) as in_file:
        latest_version = in_file.read()
    return int(latest_version) + 1

def update(args):
    version = get_next_version()
    print("Updating the repo")

    update_file = os.path.join(CWD, "updater", "versions", "update-{0}.py".format(version))

    if not os.path.exists(update_file):
        print("Update file does not exist. Will not update.")
        return

    call(["gpg", "-u", GPG_KEY_ID, "-a", "-b", update_file])

    repo = git.Repo(CWD)
    repo.git.add("updater/versions/")
    if repo.is_dirty():
        repo.git.commit("-a", m="Automatic update to version {0}".format(version))
        print("Pushing changes to remote")
        repo.git.push("-u", "origin", "master")
        print("Creating a new release with version {0}".format(version))
        create_new_release(str(version))

def parse_args():
    parser = argparse.ArgumentParser(description="Handle the workflow for lepidopter updater")
    subparsers = parser.add_subparsers()

    parser_update = subparsers.add_parser("update")
    parser_update.set_defaults(func=update)

    args = parser.parse_args()
    args.func(args)

def main():
    parse_args()

if __name__ == "__main__":
    main()
