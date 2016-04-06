#!/bin/sh
workspace=$(mktemp -d /tmp/armada-vagrant-XXX)
output=${1-$workspace/armada.box}

cp -r ./src/remote_scripts/* "$workspace"
cd "$workspace" || exit

trap 'vagrant destroy --force' EXIT
vagrant up
vagrant package --output "$output"
