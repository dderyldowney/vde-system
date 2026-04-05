#!/usr/bin/env zsh
# VDE Initialization Script: haskell
# USP compliant - strictly ZSH
# Forged in Beskar

# 1. THE PACKAGE ALLOY: Define requirements with unique local prefix
local vde_haskell_pkgs="ghc cabal-install"

# 2. THE FORGE WORK: Update and install
apt-get update
apt-get install -y ${=vde_haskell_pkgs}

# 3. PURGING THE GHOSTS: Cleanup apt artifacts
apt-get clean
rm -rf /var/lib/apt/lists/*
