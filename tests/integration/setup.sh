#!/bin/sh
mkdir -p /etc/default
cat << EOF > /etc/default/lepidopter
LEPIDOPTER_BUILD="alpha"
EOF
