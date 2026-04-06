#!/usr/bin/env zsh
# VDE USP Hydration Script: haskell
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_haskell_pkgs="ghc cabal-install"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_haskell_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
