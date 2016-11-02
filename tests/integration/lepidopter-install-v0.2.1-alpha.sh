#!/bin/sh
# This file was edited also manually.

export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true
export LC_ALL=C LANGUAGE=C LANG=C

# These were added
LEPIDOPTER_REPO_PATH=/opt/lepidopter/
export DEB_RELEASE="jessie"
export APT_MIRROR="http://httpredir.debian.org/debian"
export ARCH="amd64"
export MIRROR="http://httpredir.debian.org/debian"
export HOSTNAME_IMG="lepidopter"

set -x
set -e # Exit on first error

apt-get install -y netbase ntp less openssh-server git-core \
                   binutils ca-certificates wget kmod curl \
                   haveged lsb-release tcpdump
# XXX disable localepurge as the interactive setup creates problems
# localepurge
#ROOTDIR="$1"

# Install non-free binary blob and kernel needed to boot Raspberry Pi
# wget https://raw.github.com/Hexxeh/rpi-update/master/rpi-update \
#     -O ${ROOTDIR}/usr/local/sbin/rpi-update
# chmod a+x ${ROOTDIR}/usr/local/sbin/rpi-update
# mkdir -p ${ROOTDIR}/lib/modules
# touch ${ROOTDIR}/boot/start.elf
#  Do not try to update itself, avoid making backups, skip warnings
# export UPDATE_SELF=0 SKIP_BACKUP=1 SKIP_WARNING=1
# chroot ${ROOTDIR} rpi-update

# Add module for hardware RNG
# cat <<EOF >> ${ROOTDIR}/etc/modules
# bcm2708_rng
# EOF

# Add an apt repository with apt preferences
set_apt_sources() {
    SUITE="$1"
    PIN_PRIORITY="$2"
    COMPONENTS="main"
    cat <<EOF >> /etc/apt/sources.list
# Repository: $SUITE
deb $APT_MIRROR $SUITE $COMPONENTS
EOF
    if [ -n "$PIN_PRIORITY" ]
      then
        cat <<EOF > /etc/apt/preferences.d/${SUITE}.pref
Package: *
Pin: release n=$SUITE
Pin-Priority: $PIN_PRIORITY
EOF
    fi
}

echo "Add Debian ${DEB_RELEASE}-backports repository"
set_apt_sources ${DEB_RELEASE}-backports
echo "Add Debian stretch repository"
set_apt_sources stretch 100

# Create ooniprobe log directory
mkdir -p /var/log/ooni/

# Copy required scripts, cronjobs and config files to lepidopter
# Rsync Directory/file hieratchy to image
rsync -avp $LEPIDOPTER_REPO_PATH/lepidopter-fh/ /

# Install the version of ooniprobe in alpha
pip install ooniprobe=="1.4.1"

# Install ooniprobe via setup script
/setup-ooniprobe.sh
rm /setup-ooniprobe.sh

# Execute cleanup script
/cleanup.sh
rm /cleanup.sh

# Remove SSH host keys and add regenerate_ssh_host_keys SYSV script
#/remove_ssh_host_keys.sh
# Don't regenerate ssh keys
rm /etc/init.d/regenerate_ssh_host_keys
rm /remove_ssh_host_keys.sh

# Remove motd file and create symlink for lepidopter dynamic MOTD
rm /etc/motd
ln -s /var/run/motd /etc/motd

# Add (optional) pluggable transport support in tor config
cat $LEPIDOPTER_REPO_PATH/conf/tor-pt.conf >> /etc/tor/torrc

useradd -G sudo lepidopter
echo "lepidopter:lepidopter"|chpasswd

echo "Customize script finished successfully."
exit 0
