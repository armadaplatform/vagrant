#!/bin/bash

set -e

OUTPUT_FILE="${WORKSPACE}/armada.box"
echo "WORKSPACE: ${WORKSPACE}"
echo "OUTPUT_FILE: ${OUTPUT_FILE}"

if [ -f "${OUTPUT_FILE}" ]; then
    echo "ERROR: ${OUTPUT_FILE} already exists."
    exit 1
fi

mkdir -p "${WORKSPACE}"
cd "${WORKSPACE}"

vagrant up --no-provision
if [ -n "${http_proxy}" ]; then
    echo "Setting http_proxy to ${http_proxy} inside vm..."
    echo "echo export http_proxy=\"${http_proxy}\" >> /tmp/pre_bootstrap.sh" | vagrant ssh
fi
vagrant provision
vagrant package --output "${OUTPUT_FILE}"
vagrant destroy --force
