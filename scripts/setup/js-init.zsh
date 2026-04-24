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
typeset vde_js_pkgs="curl git build-essential docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_js_pkgs}

# Setup Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/setup_node.sh
sh /tmp/setup_node.sh
apt-get install -y nodejs

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -f /tmp/setup_node.sh
