#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: kotlin
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_kotlin_pkgs="default-jdk-headless curl zip unzip vim git docker.io"

# 2. THE FORGE WORK
apt-get update
# Missing man1 dir fix
mkdir -p /usr/share/man/man1
apt-get install -y ${=vde_kotlin_pkgs}

# SDKMAN INITIALIZATION
local dev_home=~devuser
export SDKMAN_DIR="${dev_home}/.sdkman"
export sdkman_auto_answer=true

# Force clean start if directory is a ghost
if [[ -d "$SDKMAN_DIR" && ! -f "$SDKMAN_DIR/bin/sdkman-init.sh" ]]; then
    rm -rf "$SDKMAN_DIR"
fi

# Install SDKMAN as devuser
if [[ ! -d "$SDKMAN_DIR" ]]; then
    su devuser -c 'curl -s "https://get.sdkman.io?rcupdate=false" | zsh'
fi

# Hydration
local _sdk_init="$SDKMAN_DIR/bin/sdkman-init.sh"
if [[ -f "$_sdk_init" ]]; then
    su devuser -c "source $_sdk_init && sdk install kotlin < /dev/null"
fi

# 3. PERSISTENCE ANCHOR
local _zshenv="${dev_home}/.zshenv"
mkdir -p "${dev_home}"
touch "${_zshenv}"
grep -q "SDKMAN_DIR" "${_zshenv}" || {
    {
        echo "export SDKMAN_DIR=\"$SDKMAN_DIR\""
        echo "[[ -s \"$_sdk_init\" ]] && source \"$_sdk_init\""
    } >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
