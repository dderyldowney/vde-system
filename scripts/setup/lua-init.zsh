#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: lua
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_lua_pkgs="lua5.4 luarocks git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_lua_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
