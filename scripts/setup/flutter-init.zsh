#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: flutter
# ZSH-native shibboleth (Rule 1)
local _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

local dev_home=$HOME

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_flutter_pkgs="curl git unzip xz-utils zip libglu1-mesa docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_flutter_pkgs}

# Setup Flutter for devuser
su devuser -c "if [[ ! -d \"${dev_home}/flutter\" ]]; then git clone --depth 1 https://github.com/flutter/flutter.git ${dev_home}/flutter; fi && export PATH=\"\$PATH:${dev_home}/flutter/bin\" && ${dev_home}/flutter/bin/flutter precache"

# 3. PERSISTENCE ANCHOR
local _zshenv="${dev_home}/.zshenv"
mkdir -p ${dev_home}
touch "${_zshenv}"
grep -q "flutter/bin" "${_zshenv}" || {
    echo "export PATH=\"\$PATH:${dev_home}/flutter/bin\"" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
