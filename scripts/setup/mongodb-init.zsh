#!/usr/bin/env zsh
# VDE USP Hydration Ritual: mongodb
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_mongodb_pkgs="mongodb-org-shell mongodb git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_mongodb_pkgs}

# 3. PERSISTENCE ANCHOR (ONLY FOR SERVICES: mysql, redis, mongodb, rabbitmq, couchdb, nginx, postgres)
# Append start command to devuser's .zshenv if not present
local _zshenv="/home/devuser/.zshenv"
if [[ "true" == "true" ]]; then
    mkdir -p /home/devuser
    touch "${_zshenv}"
    grep -q "service mongodb start" "${_zshenv}" || echo "sudo service mongodb start >/dev/null 2>&1" >> "${_zshenv}"
    chown devuser:devuser "${_zshenv}"
fi

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
