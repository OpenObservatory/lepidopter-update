import os
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
GPG_KEY_ID = "0xC3ECDC04204F9D29"

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
        print(r.json())
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

def create_new_release(version, skip_signing=False, force=False):
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
    if force is False:
        print("Creating a new release with version {0}".format(version))
        r = requests.post(GH_BASE_URL + "/releases",
                params=params, json=data)
        try:
            assert r.status_code == 201
        except:
            print r.text
            return
    else:
        r = requests.get(GH_BASE_URL + "/releases/tags/" + str(version),
                         params=params)
        assert r.status_code == 200

    j = r.json()
    upload_url = j["upload_url"].replace("{?name,label}", "")
    update_file = "updater/versions/update-{0}.py".format(version)
    update_file_sig = "updater/versions/update-{0}.py.asc".format(version)
    content_type = "text/plain"

    if force is True:
        r = requests.get(GH_BASE_URL + "/releases/%s/assets" % j["id"],
                         params=params)
        assert r.status_code == 200
        j = r.json()
        for asset in j:
            print("Deleting %s" % asset['url'])
            r = requests.delete(asset['url'], params=params)
            assert r.status_code == 204

    data = open(update_file, "r").read()
    _upload_asset(upload_url,
                  name="update.py",
                  content_type=content_type,
                  data=data)

    if skip_signing is not True:
        data = open(update_file_sig, "r").read()
        _upload_asset(upload_url,
                    name="update.py.asc",
                    content_type=content_type,
                    data=data)

    if force is False:
        update_latest_version(str(version))

def get_next_version():
    with open(os.path.join(CWD, "updater", "latest_version")) as in_file:
        return int(in_file.read()) + 1

def write_version(version):
    with open(os.path.join(CWD, "updater", "latest_version"), "w") as out_file:
        out_file.write(str(version))

def update(args, version=None, force=False):
    if version is None:
        version = get_next_version()
    print("Updating the repo to %s" % version)

    update_file = os.path.join(CWD, "updater", "versions", "update-{0}.py".format(version))

    if not os.path.exists(update_file):
        print("Update file (%s) does not exist. Will not update." % update_file)
        return

    if args.skip_signing is not True:
        call(["gpg", "--batch", "-u", GPG_KEY_ID, "-a", "-b", update_file])

    if force is False:
        write_version(version)
    repo = git.Repo(CWD)
    repo.git.add("updater/versions/")
    repo.git.add("updater/latest_version")
    if repo.is_dirty():
        commit_message = "Automatic update to version {0}".format(version)
        if force is True:
            commit_message = "Rewriting version {0}".format(version)
        repo.git.commit("-a", m=commit_message)
        print("Pushing changes to remote")
        repo.git.push("-u", "origin", "master")
        create_new_release(str(version),
                           skip_signing=args.skip_signing,
                           force=force)

def rewrite(args, **kw):
    next_version = get_next_version()
    for version in range(1, next_version):
        print("Force updating {0}".format(version))
        update(args, version=version, force=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Handle the workflow for lepidopter updater")
    subparsers = parser.add_subparsers()

    parser_update = subparsers.add_parser("update")
    parser_update.add_argument('--skip-signing',
                               action='store_true',
                               help="Skip signing the version file (to be used for development)")
    parser_update.add_argument('--force',
                               action='store_true',
                               help="Force updating of the version")
    parser_update.set_defaults(func=update)
    parser_rewrite = subparsers.add_parser("rewrite", help="rewrite all the updates")
    parser_rewrite.add_argument('--skip-signing',
                               action='store_true',
                               help="Skip signing the version file (to be used for development)")
    parser_rewrite.set_defaults(func=rewrite)

    args = parser.parse_args()
    args.func(args, force=args.force)

def main():
    parse_args()

if __name__ == "__main__":
    main()
