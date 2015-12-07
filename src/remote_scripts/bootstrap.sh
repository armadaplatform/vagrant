#!/bin/bash

set -e

if [ -f /tmp/pre_bootstrap.sh ]; then
    source /tmp/pre_bootstrap.sh
fi

sed -i 's/http:\/\/us.archive.ubuntu.com/http:\/\/archive.ubuntu.com/g' /etc/apt/sources.list
echo "set grub-pc/install_devices /dev/sda" | debconf-communicate

apt-get update
apt-get upgrade -y

#--- Install additional tools.
apt-get install -y git mc jq curl

#--- Install Docker.
curl -sSL https://get.docker.com/ | sh
usermod -a -G docker vagrant

if [ -n "${http_proxy}" ]; then
    echo "Setting http_proxy to ${http_proxy} in /etc/default/docker"
    echo export http_proxy="${http_proxy}" >> /etc/default/docker
    service docker restart
fi

#--- Install Armada.
bash <(curl -sL http://armada.sh/install)
service armada stop

if [ -n "${http_proxy}" ]; then
    sed -i '/http_proxy/d' /etc/default/docker
    service docker restart
fi

apt-get clean -y
apt-get autoclean -y
apt-get autoremove -y
dd if=/dev/zero of=/EMPTY bs=1M 2> /dev/null || true
rm -f /EMPTY
