#!/usr/bin/env zsh
# VDE USP Hydration Script: testcfgcustompkg
# Forged via add-vm-type

# 1. THE PACKAGE ALLOY
# Define packages here
local vde_pkgs=""

# 2. THE FORGE WORK
echo test

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
