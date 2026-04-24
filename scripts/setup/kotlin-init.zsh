#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: kotlin
# ZSH-native shibboleth (Rule 1)
local _ZSH_PURE=${(%):-%x}

# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_kotlin_pkgs="curl git unzip zip"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_kotlin_pkgs} default-jdk

# 3. KOTLIN INSTALLATION (Hardened Home)
local dev_home="/home/devuser"
mkdir -p "${dev_home}"

if [[ ! -d "${dev_home}/.sdkman" ]]; then
    echo "[VDE-KOTLIN] Installing SDKMAN..."
    # Install SDKMAN as devuser
    sudo -u devuser curl -s "https://get.sdkman.io" | sudo -u devuser bash
fi

# 4. PERSISTENCE ANCHOR
local _zshenv="${dev_home}/.zshenv"
{
    echo 'export SDKMAN_DIR="${HOME}/.sdkman"'
    echo '[[ -s "${SDKMAN_DIR}/bin/sdkman-init.sh" ]] && source "${SDKMAN_DIR}/bin/sdkman-init.sh"'
} >> "${_zshenv}"

# Set ownership
chown -R devuser:devuser "${dev_home}"

# 5. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
