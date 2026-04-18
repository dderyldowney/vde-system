#!/usr/bin/env zsh
# VDE USP Hydration Script: mean
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_mean_pkgs="curl git build-essential docker.io mongodb-clients"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_mean_pkgs}

# Setup Node.js via NodeSource (Hydrated from js-init.zsh logic)
curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/setup_node.sh
sh /tmp/setup_node.sh
apt-get install -y nodejs

# 3. CLUSTER COORDINATION
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
grep -q "MONGO_URI" "${_zshenv}" || {
    echo "export MONGO_URI=mongodb://vde-mongodb:27017" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"
echo "[VDE-CLUSTER] Awareness established: Spoke 'mean' is linked to 'vde-mongodb'."

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -f /tmp/setup_node.sh
