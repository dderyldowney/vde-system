#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: mean
# ZSH-native shibboleth (Rule 1)
local _ZSH_PURE=${(%):-%x}

# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_mean_pkgs="curl git gnupg"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_mean_pkgs}

# 3. NODEJS INSTALLATION
if ! command -v node >/dev/null 2>&1; then
    echo "[VDE-MEAN] Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
fi

# 4. MONGODB SHELL (Hardened Source)
if ! command -v mongosh >/dev/null 2>&1; then
    echo "[VDE-MEAN] Installing MongoDB Shell..."
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/mongodb-server-7.0.gpg
    echo "deb [ signed-by=/etc/apt/trusted.gpg.d/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    apt-get update
    apt-get install -y mongodb-mongosh
fi

# 5. CLUSTER COORDINATION
local dev_home="/home/devuser"
local _zshenv="${dev_home}/.zshenv"
mkdir -p ${dev_home}
touch "${_zshenv}"
grep -q "MONGO_URI" "${_zshenv}" || {
    echo "export MONGO_URI=mongodb://mongodb:27017" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"
echo "[VDE-CLUSTER] Awareness established: Spoke 'mean' is linked to 'mongodb'."

# 6. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
