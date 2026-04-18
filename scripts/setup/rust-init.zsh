#!/usr/bin/env zsh
# VDE USP Hydration Ritual: rust
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
#
# Release: Sovereign Baseline 1.4.1
# Objective: Hardened build-time hydration with Rust Mirror verification.

set -e

# 1. THE PACKAGE ALLOY
# Define system-level dependencies for Rust development and build-time hydration.
export DEBIAN_FRONTEND=noninteractive
local vde_rust_pkgs="build-essential curl git pkg-config libssl-dev ca-certificates docker.io"

# 2. THE FORGE WORK
# Perform the physical smelting of system packages.
apt-get update
apt-get install -y ${=vde_rust_pkgs}

# Rust-Specific Smelting: Install rustup via the Sovereign Mirror.
# This ensures the Spoke is "Born Ready" (BTO) at image creation.
# Using the standard mirror with hardened TLS requirements.
# We ensure the home directory exists before installation.
mkdir -p /home/devuser
chown devuser:devuser /home/devuser

sudo -u devuser sh -c 'if ! command -v rustc >/dev/null; then \
  curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path; \
fi'

# 3. PERSISTENCE ANCHORS (User Personalization & Shell Integration)
# Injects pathing and environment variables into .zshenv.
# These anchors ensure that the Rust toolchain and Sovereign Bridge 
# survive 'vde rebuild' and 'vde stop/start' cycles.
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"

# Anchor: Rust Toolchain Pathing
# Ensures cargo and rustc are available immediately upon 'vde enter'.
grep -q "cargo/env" "${_zshenv}" || {
  echo 'source $HOME/.cargo/env' >> "${_zshenv}"
}

# Anchor: Sovereign SSH Bridge identity 
# Mandated by the Rule Spine for Git operations using host keys.
grep -q "SSH_AUTH_SOCK" "${_zshenv}" || {
  echo 'if [[ -z "${SSH_AUTH_SOCK}" ]]; then export SSH_AUTH_SOCK="/home/devuser/.ssh/vde/agent.sock"; fi' >> "${_zshenv}"
}

chown devuser:devuser "${_zshenv}"

# 4. PURGING THE GHOSTS
# Clean up build artifacts to maintain a hardened, immutable baseline.
apt-get clean
rm -rf /var/lib/apt/lists/*
