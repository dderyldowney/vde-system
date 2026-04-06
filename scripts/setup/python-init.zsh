#!/usr/bin/env zsh
# VDE USP Hydration Script: python
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_python_pkgs="python3 python3-pip python-is-python3 postgresql-client"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_python_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
