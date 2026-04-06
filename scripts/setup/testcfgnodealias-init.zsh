#!/usr/bin/env zsh
# VDE USP Hydration Script: testcfgnodealias
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_testcfgnodealias_pkgs=""

# 2. THE FORGE WORK
# echo install nodejs from original test
echo "installing nodejs"

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
