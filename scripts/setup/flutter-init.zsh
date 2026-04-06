#!/usr/bin/env zsh
# VDE USP Hydration Script: flutter
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_flutter_pkgs="curl git unzip xz-utils zip libglu1-mesa"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_flutter_pkgs}

# Setup Flutter for devuser
su devuser -c 'if [ ! -d "/home/devuser/flutter" ]; then git clone --depth 1 https://github.com/flutter/flutter.git /home/devuser/flutter; fi && export PATH="$PATH:/home/devuser/flutter/bin" && /home/devuser/flutter/bin/flutter precache'

# 3. PERSISTENCE ANCHOR
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
grep -q "flutter/bin" "${_zshenv}" || {
    echo 'export PATH="$PATH:/home/devuser/flutter/bin"' >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
