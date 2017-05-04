"""
This is the auto update script for going from version 7 to version 8.
"""

import logging

from subprocess import check_call

__version__ = "8"

TXTORCON_PIP_URL = "txtorcon==0.18.0"
WATCHDOG_CONF = """
#ping			= 172.31.14.1
#ping			= 172.26.1.255
#interface		= eth0
#file			= /var/log/messages
#change			= 1407

# Uncomment to enable test. Setting one of these values to '0' disables it.
# These values will hopefully never reboot your machine during normal use
# (if your machine is really hung, the loadavg will go much higher than 25)
#max-load-1		= 24
#max-load-5		= 18
#max-load-15		= 12

# Note that this is the number of pages!
# To get the real size, check how large the pagesize is on your machine.
#min-memory		= 1
#allocatable-memory	= 1

#repair-binary		= /usr/sbin/repair
#repair-timeout		= 
#test-binary		= 
#test-timeout		= 

watchdog-device		= /dev/watchdog
# Avoid cannot set timeout warning 
watchdog-timeout	= 10

# Defaults compiled into the binary
#temperature-device	=
#max-temperature	= 120

# Defaults compiled into the binary
#admin			= root
interval		= 2
#logtick                = 1
#log-dir		= /var/log/watchdog

# This greatly decreases the chance that watchdog won't be scheduled before
# your machine is really loaded
realtime		= yes
priority		= 1

# Check if rsyslogd is still running by enabling the following line
#pidfile		= /var/run/rsyslogd.pid   
"""

SUDOERS_CONF= """
#
# This file MUST be edited with the 'visudo' command as root.
#
# Please consider adding local content in /etc/sudoers.d/ instead of
# directly modifying this file.
#
# See the man page for details on how to write a sudoers file.
#
Defaults	env_reset
Defaults	mail_badpass
Defaults	secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Host alias specification

# User alias specification

# Cmnd alias specification

# User privilege specification
root	ALL=(ALL:ALL) ALL

# Allow members of group sudo to execute any command
%sudo	ALL=(ALL:ALL) NOPASSWD: ALL

# See sudoers(5) for more information on "#include" directives:

#includedir /etc/sudoers.d
"""

MOTD_HEAD = """
[93m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Oo@:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@8:::o8@@@@@Oc@@@@@@Oc:::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@:::o::::o@8O@o@8::::cc::c@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@c::c@@c:::c@@@::::o@O:::o@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@O::::oo::::C@c::::C:::::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@o:::::::::8@o:::::::::O@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@O:c:::c:c@@8:::c:::c@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@o:::::::o@c:::::::O@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@8::::c:::C@:::c::::c@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@C::::::c@@@@8:::::::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OCO@@@@@@@@@@@@8CC8@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@[0m
[36m@@Co@@@@@@@@@@@@@@@@@@@@@@@@@:O@@@@@@O:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@oc@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@O.@@@@@@@@@@@@@@@@@@@@oc@@@@@@@@@@@@@@@@@@@
@@oc@@@@@@@O:coo:C@@:ccoo:o@@.O@O:coo::@@O.ooo:O@@:::oc:c@o::c8@c:co::O@c::::8@@
@@oc@@@@@@8.@@@@@co@:C@@@@:C@:OO.@@@@O.@C:@@@@@cC@cc@@@@:c@oc@@::@@@@8:8C:O@@@@@
@@oc@@@@@@O:888888@@:C@@@@co@:OC:@@@@O.@oc@@@@@co@:c@@@@cc@cc@@::OOOOOO@C:8@@@@@
@@o:888888@cc@@@Cc@@::O@@C.@@:O@:o@@O::@@:o@@@o:@@c:o@@C:C@o:@@O:o@@8co@C:8@@@@@
@@@@@@@@@@@@@@88@@@@:C@88@@@@@@@@@88@@@@@@@@8@@@@@cc@OO8@@@@8C8@@@OCO@@@@8@@@@@@
@@@@@@@@@@@@@@@@@@@@:C@@@@@@@@@@@@@@@@@@@@@@@@@@@@:c@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@[0m
"""

BOOT_CONFIG = """
# Minimal (with no vc_vchi_sm_init failure) GPU memory for headless mode
gpu_mem=32
# Enable the hardware watchdog
dtparam=watchdog=on
# Turn power LED into heartbeat
dtparam=pwr_led_trigger=heartbeat
# Enable the hardware random number generator (RNG)
dtparam=random=on
"""
WATCHDOG_CONF_PATH = "/etc/watchdog.conf"
SUDOERS_CONF_PATH = "/etc/sudoers"
MOTD_HEAD_PATH = "/etc/motd.head"
BOOT_CONFIG_PATH = "/boot/config.txt"

def write_watchdog_conf():
    with open(WATCHDOG_CONF_PATH, "w") as out_file:
        out_file.write(WATCHDOG_CONF)

def write_sudoers_conf():
    with open(SUDOERS_CONF_PATH, "w") as out_file:
        out_file.write(SUDOERS_CONF)

def write_motd_head():
    with open(MOTD_HEAD_PATH, "w") as out_file:
        out_file.write(MOTD_HEAD)

def write_boot_config():
    with open(BOOT_CONFIG_PATH, "w") as out_file:
        out_file.write(BOOT_CONFIG)

def _perform_update():
    check_call(["apt-get", "-q", "update"])
    # Install OpenVPN package without starting the OpenVPN service
    check_call(["apt-get", "-y", "install", "openvpn"], env={"RUNLEVEL": "1"})
    # Disable OpenVPN systemd unit
    check_call(["systemctl", "disable", "openvpn"])

    # Install newest e2fsprogs due to incompatibly with ext4 file system checks
    check_call(["apt-get", "-y", "install", "-t", "jessie-backports", "e2fsprogs"])
    # Install obfs4proxy (includes a lite version of meek)
    check_call(["apt-get", "-y", "install", "-t", "stretch", "obfs4proxy"])
    # Remove old system versions of python-openssl
    check_call(["apt-get", "-y", "remove", "python-openssl"])

    # Remove bcm2708_rng entry as modules are now handled by /boot/config.txt
    check_call(["cp", "-b", "/etc/modules", "/etc/modules.bak"])
    check_call(["sed", "-i",  "'/bcm2708_rng/d'", "/etc/modules"])

    # Mount option noatime disables file access writes every time a file is read
    check_call(["sed", "-i", "'s/\/ ext4/\/ ext4 defaults,noatime/'", "/etc/fstab"])

    # Fix active meek tor bridges
    check_call(["sed", "-i", "'s/az786092.vo.msecnd.net/meek.azureedge.net/'", "/etc/tor/torrc"])

    # txtorcon bug in 0.19.0 - https://github.com/meejah/txtorcon/issues/227
    check_call(["pip", "install", TXTORCON_PIP_URL])

    write_watchdog_conf()
    write_sudoers_conf()
    write_motd_head()
    write_boot_config()

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
