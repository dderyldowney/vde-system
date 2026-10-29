#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Script: js
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_js_pkgs="curl git gnupg ca-certificates build-essential docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_js_pkgs}

# Load the core library first so the shared curl bounds are available.
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }

# Setup Node.js via NodeSource (zsh-native apt repo; no vendor shell script).
# Equivalent to NodeSource's documented manual install: fetch the signing key,
# dearmor it into a keyring, and add the signed deb source for Node 22.
typeset _node_major=22
typeset _node_key=$(mktemp)
mkdir -p /etc/apt/keyrings
curl -fsSL "${VDE_CURL_BOUNDS[@]}" \
    https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key -o "${_node_key}"
[[ -s "${_node_key}" ]] || { print -u2 "NodeSource key download failed or empty"; exit 1; }
gpg --dearmor --yes -o /etc/apt/keyrings/nodesource.gpg "${_node_key}"
# apt reads the keyring as the unprivileged _apt user; make it world-readable.
chmod 644 /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${_node_major}.x nodistro main" \
    > /etc/apt/sources.list.d/nodesource.list
apt-get update
apt-get install -y nodejs

# 3. PURGING THE GHOSTS (Rule 12.5)
vde_purge_ghosts
rm -f "${_node_key}"
