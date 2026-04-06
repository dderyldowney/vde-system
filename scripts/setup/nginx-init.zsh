#!/usr/bin/env zsh
# VDE USP Hydration Ritual: nginx
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_nginx_pkgs="nginx-extras"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_nginx_pkgs}

# 3. PERSISTENCE ANCHOR (ONLY FOR SERVICES: mysql, redis, mongodb, rabbitmq, couchdb, nginx, postgres)
# Append start command to devuser's .zshenv if not present
local _zshenv="/home/devuser/.zshenv"
if [[ "true" == "true" ]]; then
    mkdir -p /home/devuser
    touch "${_zshenv}"
    grep -q "service nginx start" "${_zshenv}" || echo "sudo service nginx start >/dev/null 2>&1" >> "${_zshenv}"
    chown devuser:devuser "${_zshenv}"
fi

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
