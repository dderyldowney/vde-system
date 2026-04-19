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
sudo -u devuser sh -c 'if ! command -v rustc >/dev/null; then \
  curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path; \
fi'

# 3. PERSISTENCE ANCHORS (User Personalization & Shell Integration)
# Injects pathing and environment variables into .zshenv and .zshrc.
# These anchors ensure that the Rust toolchain and Sovereign Bridge 
# survive 'vde rebuild' and 'vde stop/start' cycles.
local dev_home=~devuser
local _zshenv="${dev_home}/.zshenv"
local _zshrc="${dev_home}/.zshrc"

touch "${_zshenv}" "${_zshrc}"

# Anchor: Rust Toolchain Pathing
# Ensures cargo and rustc are available immediately upon 'vde enter'.
# .zshenv handles environment for all shells (mandated for non-interactive tools).
grep -q "cargo/bin" "${_zshenv}" || {
  echo "export PATH=\"\${dev_home}/.cargo/bin:\$PATH\"" >> "${_zshenv}"
}

# .zshrc ensures interactive shell path inheritance and prioritization.
# This fixes IS171 where Cargo was missing in interactive devuser sessions.
grep -q "cargo/bin" "${_zshrc}" || {
  echo '' >> "${_zshrc}"
  echo '# Rust Toolchain' >> "${_zshrc}"
  echo "export PATH=\"\${dev_home}/.cargo/bin:\$PATH\"" >> "${_zshrc}"
}

# Anchor: Sovereign SSH Bridge identity 
# Mandated by the Rule Spine for Git operations using host keys.
grep -q "SSH_AUTH_SOCK" "${_zshenv}" || {
  echo "if [[ -z \"\${SSH_AUTH_SOCK}\" ]]; then export SSH_AUTH_SOCK=\"\${dev_home}/.ssh/vde/agent.sock\"; fi" >> "${_zshenv}"
}

chown devuser:devuser "${_zshenv}" "${_zshrc}"

# 4. PURGING THE GHOSTS
# Clean up build artifacts to maintain a hardened, immutable baseline.
apt-get clean
rm -rf /var/lib/apt/lists/*
