#!/usr/bin/env zsh
# VDE Initialization Script: c
# USP compliant - strictly ZSH
# Forged in Beskar

# 1. THE PACKAGE ALLOY: Define requirements with unique local prefix
local vde_c_pkgs="gcc make cmake gdb"

# 2. THE FORGE WORK: Update and install
apt-get update
apt-get install -y ${=vde_c_pkgs}

# 3. PURGING THE GHOSTS: Cleanup apt artifacts
apt-get clean
rm -rf /var/lib/apt/lists/*
