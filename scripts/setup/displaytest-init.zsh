#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: displaytest
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_displaytest_pkgs="golang-go git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_displaytest_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
