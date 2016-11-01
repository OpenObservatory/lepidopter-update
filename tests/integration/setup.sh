#!/bin/sh
mkdir -p /etc/default/lepidopter
cat << EOF > /etc/default/lepidopter
LEPIDOPTER_BUILD="alpha"
EOF
