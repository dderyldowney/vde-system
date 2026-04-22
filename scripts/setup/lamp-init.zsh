#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: lamp
# ZSH-native shibboleth (Rule 1)
local _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_lamp_pkgs="php php-cli php-xml php-mbstring php-curl composer default-mysql-client git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_lamp_pkgs}

# 3. CLUSTER COORDINATION
local dev_home=~devuser
local _zshenv="${dev_home}/.zshenv"
mkdir -p "${dev_home}"
touch "${_zshenv}"
grep -q "DB_HOST" "${_zshenv}" || {
    echo "export DB_HOST=vde-mysql" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"
echo "[VDE-CLUSTER] Awareness established: Spoke 'lamp' is linked to 'vde-mysql' and 'vde-nginx'."

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
