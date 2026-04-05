#!/usr/bin/env zsh
# VDE USP Hydration Script: testcfggodisp
# Forged via add-vm-type

# 1. THE PACKAGE ALLOY
# Define packages here
local vde_pkgs=""

# 2. THE FORGE WORK
apt-get install -y golang

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
