#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Ritual: rust
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
#
# Release: Sovereign Baseline 1.5.1
# Objective: Hardened build-time hydration with Rust Mirror verification.

set -e

# 1. THE PACKAGE ALLOY
# Define system-level dependencies for Rust development and build-time hydration.
export DEBIAN_FRONTEND=noninteractive
typeset vde_rust_pkgs="build-essential curl git pkg-config libssl-dev ca-certificates docker.io"

# 2. THE FORGE WORK
# Perform the physical smelting of system packages.
apt-get update
apt-get install -y ${=vde_rust_pkgs}

# Rust-Specific Smelting: Install rustup via the Sovereign Mirror.
# This ensures the Spoke is "Born Ready" (BTO) at image creation.
# Mandate C (ZSH ONLY): run rustup's NATIVE installer binary directly instead
# of piping the vendor shell script to `sh`. The rustup-init binary does exactly
# what `sh.rustup.rs | sh` does, so no foreign shell is invoked (parity with the
# pyenv Spoke). TLS stays hardened and downloads are time-bounded; the shared
# helper lives in lib/vde-core (Signet #598).
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }
vde_install_rustup devuser VDE-RUST

# 3. PERSISTENCE ANCHORS
# Direct injection as commanded by the Clan Leader.
# Ensures the cargo path is the UNIQUE and VERY LAST LINE of $HOME/.zshrc and $HOME/.zshenv.

sudo -H -u devuser zsh -c '
    # Ensure configuration files exist
    touch ~/.zshenv ~/.zshrc

    # Purge existing entries to ensure uniqueness
    sed -i "/\.cargo\/bin/d" ~/.zshenv
    sed -i "/\.cargo\/bin/d" ~/.zshrc

    # Append the mandated path export to the end of the files
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshenv
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshrc
'

# 3.5. COMPONENT HYDRATION
# Install rust-analyzer as devuser, with cargo/bin already on PATH from the
# persistence anchors above. Must run after .zshrc/.zshenv are written.
sudo -H -u devuser zsh -c '
    export PATH="$HOME/.cargo/bin:$PATH"
    rustup component add rust-analyzer
    rustup component add rust-src
'

# 4. PURGING THE GHOSTS (Rule 12.5)
# Clean up build artifacts to maintain a hardened, immutable baseline.
vde_purge_ghosts
