#!/usr/bin/env zsh
# VDE USP Hydration Script: testcfgcustompkg
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_testcfgcustompkg_pkgs=""

# 2. THE FORGE WORK
apt-get update
apt-get install -y python3 python3-pip my-package && touch /tmp/vde-custom-pkg-marker

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
