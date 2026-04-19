#!/usr/bin/env zsh
# VDE USP Hydration Script: csharp
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_csharp_pkgs="curl libicu-dev ca-certificates git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_csharp_pkgs}

# Setup .NET
DOTNET_INSTALL_DIR="/usr/share/dotnet"
mkdir -p "${DOTNET_INSTALL_DIR}"
curl -sSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh
sh /tmp/dotnet-install.sh --version 8.0.100 --install-dir "${DOTNET_INSTALL_DIR}"
ln -sf "${DOTNET_INSTALL_DIR}/dotnet" /usr/bin/dotnet

# 3. PERSISTENCE ANCHOR
local dev_home=~devuser
local _zshenv="${dev_home}/.zshenv"
mkdir -p "${dev_home}"
touch "${_zshenv}"
grep -q "DOTNET_ROOT" "${_zshenv}" || {
    echo "export DOTNET_ROOT=${DOTNET_INSTALL_DIR}" >> "${_zshenv}"
    echo "export PATH=\$PATH:${DOTNET_INSTALL_DIR}" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -f /tmp/dotnet-install.sh
