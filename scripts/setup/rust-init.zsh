#!/usr/bin/env zsh
# @armor (Spoke Hydration)
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
sudo -u devuser sh -c 'if ! command -v rustc >/dev/null; then \
  curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path; \
fi'

# 3. PERSISTENCE ANCHORS
# Direct injection as commanded by the Clan Leader.
# Ensures the cargo path is the UNIQUE and VERY LAST LINE of $HOME/.zshrc and $HOME/.zshenv.

sudo -u devuser zsh -c '
    # Ensure configuration files exist
    touch ~/.zshenv ~/.zshrc

    # Purge existing entries to ensure uniqueness
    sed -i "/\.cargo\/bin/d" ~/.zshenv
    sed -i "/\.cargo\/bin/d" ~/.zshrc

    # Append the mandated path export to the end of the files
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshenv
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshrc
'

# 4. PURGING THE GHOSTS
# Clean up build artifacts to maintain a hardened, immutable baseline.
apt-get clean
rm -rf /var/lib/apt/lists/*
