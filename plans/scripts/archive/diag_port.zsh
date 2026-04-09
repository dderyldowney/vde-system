#!/usr/bin/env zsh
source ./lib/vm-common
source ./lib/vde-docker

echo "VM_TYPES_CONF: ${VM_TYPES_CONF}"
echo "Contents of .conf around 2214:"
grep "2214" "${VM_TYPES_CONF}"

echo "Probing 2214 logic:"
port=2214
if grep -q "|${port}$" "${VM_TYPES_CONF}" 2>/dev/null; then
    echo "Port ${port} is pre-defined"
else
    echo "Port ${port} is NOT pre-defined"
fi

echo "Running find_available_ssh_port 2210 2220"
find_available_ssh_port 2210 2220
