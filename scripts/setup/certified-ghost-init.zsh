#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Script: certified-ghost
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_ghost_pkgs="htop neofetch"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_ghost_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
