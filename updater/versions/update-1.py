import os
import shutil

from subprocess import check_call

DEB_RELEASE="jessie"
TOR_DEB_REPO="http://deb.torproject.org/torproject.org"
TOR_DEB_REPO_SRC_LIST="/etc/apt/sources.list.d/tor.list"
TOR_REPO_GPG="A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89"
OONIPROBE_PIP_URL = "git+https://github.com/TheTorProject/ooni-probe@v2.0.0-alpha#egg=ooniprobe"

OONIPROBE_SYSTEMD_SCRIPT = """\
[Unit]
Description=%n, network interference detection tool
After=network.target nss-lookup.target

[Service]
Type=forking
PIDFile=/var/lib/ooni/twistd.pid
ExecStart=/usr/local/bin/ooniprobe-agent start
ExecStop=/usr/local/bin/ooniprobe-agent stop
TimeoutStartSec=300
TimeoutStopSec=60
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
OONIPROBE_SYSTEMD_PATH = "/etc/systemd/system/ooniprobe.service"

def rm_rf(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        os.remove(path)

def write_systemd_script():
    if os.path.exists(OONIPROBE_SYSTEMD_PATH):
        check_call(["service", "ooniprobe", "stop"])

    with open(OONIPROBE_SYSTEMD_PATH, "w") as out_file:
        out_file.write(OONIPROBE_SYSTEMD_SCRIPT)

def run():
    # Delete all the daily crons
    rm_rf("/etc/cron.daily/remove_upl_reports")
    rm_rf("/etc/cron.daily/run_ooniprobe_deck")
    rm_rf("/etc/cron.daily/upload_reports")
    rm_rf("/etc/cron.daily/remove_inc_reports")
    rm_rf("/etc/cron.daily/update_ooniprobe_deck")

    # XXX this is still present in the lepidopter v2 branch.
    rm_rf("/etc/cron.daily/update_ooniprobe")

    rm_rf("/etc/ooniprobe/oonireport.conf")

    rm_rf("/opt/ooni/remove-inc-reports.sh")
    rm_rf("/opt/ooni/remove-upl-reports.sh")
    rm_rf("/opt/ooni/run-ooniprobe.sh")
    rm_rf("/opt/ooni/update-deck.sh")
    rm_rf("/opt/ooni/upload-reports.sh")

    # XXX this is still present in the lepidopter v2 branch.
    rm_rf("/opt/ooni/update-ooniprobe.sh")

    # XXX it's probably redundant to run this on the first version since these
    # are probably all satisfied, but let's just be careful.
    check_call(("apt-get -y install openssl libssl-dev libyaml-dev "
               "libffi-dev libpcap-dev tor libgeoip-dev libdumbnet-dev "
               "python-dev python-pip libgmp-dev").split(" "))
    # Add Torproject Debian repository
    check_call(("apt-key adv --keyserver hkp://pool.sks-keyservers.net "
                "--recv-keys {0}".format(TOR_REPO_GPG)).split(" "))
    with open(TOR_DEB_REPO_SRC_LIST, "w") as out_file:
        out_file.write("deb {0} {1} main".format(TOR_DEB_REPO, DEB_RELEASE))
    check_call(["apt-get", "update"])

    # Install obfs4proxy that includes a lite version of meek
    check_call(["apt-get", "-y", "install", "-t", "stretch", "obfs4proxy"])

    check_call(["pip", "install", OONIPROBE_PIP_URL])

    check_call(["systemctl", "enable", "ooniprobe"])
    check_call(["systemctl", "start", "ooniprobe"])

    # XXX don't understand why setup-ooniprobe.sh does this.
    check_call(["service", "tor", "stop"])

if __name__ == "__main__":
    run()
