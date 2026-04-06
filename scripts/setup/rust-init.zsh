#!/usr/bin/env zsh
# VDE USP Hydration Script: rust
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_rust_pkgs="build-essential curl git"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_rust_pkgs}

# Setup Rust for devuser
su devuser -c 'if ! command -v rustc >/dev/null; then curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; fi'

# 3. PERSISTENCE ANCHOR
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
grep -q "cargo/env" "${_zshenv}" || {
    echo 'source $HOME/.cargo/env' >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
