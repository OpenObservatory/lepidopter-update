"""
This is the auto update script for going from version 0 to version 1.

All future lepidopter will start with version 1 already configured, so this should
not be run by them.

In order to indicate that they are configured with version 1 a file called
/etc/lepidopter-update/version with the string 1.

When this is run it will configure the pi to be already initialized and this
should not happen in future versions of lepidopter.
"""

import os
import shutil

from subprocess import check_call

OONIPROBE_PIP_URL = "https://people.torproject.org/~art/ooni/ooniprobe-2.0.0a3.tar.gz"

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

OONIPROBE_CONFIG = """
basic:
   logfile: /var/log/ooni/ooniprobe.log
advanced:
   webui_port: 8842
   webui_address: "0.0.0.0"
tor:
    data_dir: /opt/ooni/tor_data_dir
    timeout: 200
"""
OONIPROBE_CONFIG_PATH = "/etc/ooniprobe.conf"

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

def write_ooniprobe_config():
    with open(OONIPROBE_CONFIG_PATH, "w") as out_file:
        out_file.write(OONIPROBE_CONFIG)

def run():
    # Delete all the daily crons
    rm_rf("/etc/cron.daily/remove_upl_reports")
    rm_rf("/etc/cron.daily/run_ooniprobe_deck")
    rm_rf("/etc/cron.daily/upload_reports")

    # Delete all the weekly crons
    rm_rf("/etc/cron.weekly/remove_inc_reports")
    rm_rf("/etc/cron.weekly/update_ooniprobe_deck")

    # Remove unneeded cronjobs
    rm_rf("/etc/cron.daily/apt")
    rm_rf("/etc/cron.daily/dpkg")
    rm_rf("/etc/cron.daily/man-db")
    rm_rf("/etc/cron.daily/tor")

    # XXX this is still present in the lepidopter v2 branch.
    rm_rf("/etc/cron.daily/update_ooniprobe")

    rm_rf("/etc/ooniprobe/oonireport.conf")
    rm_rf("/etc/ooniprobe/ooniprobe.conf")

    rm_rf("/opt/ooni/remove-inc-reports.sh")
    rm_rf("/opt/ooni/remove-upl-reports.sh")
    rm_rf("/opt/ooni/run-ooniprobe.sh")
    rm_rf("/opt/ooni/update-deck.sh")
    rm_rf("/opt/ooni/upload-reports.sh")

    # XXX this is still present in the lepidopter v2 branch.
    rm_rf("/opt/ooni/update-ooniprobe.sh")

    # Do not access hwclock Raspberry Pi doesn't have one, use fake-hwclock
    check_call("apt-get -y install fake-hwclock" )

    write_systemd_script()
    write_ooniprobe_config()


    check_call(["pip", "install", "--upgrade", OONIPROBE_PIP_URL])

    # Set it as already initialized so we skip the informed consent on
    # pre-existing ooniprobes.
    with open("/var/lib/ooni/initialized", "w"):
        pass

    check_call(["systemctl", "enable", "ooniprobe"])
    check_call(["systemctl", "start", "ooniprobe"])

if __name__ == "__main__":
    run()
