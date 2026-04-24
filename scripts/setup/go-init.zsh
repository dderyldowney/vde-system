#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Script: go
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_go_pkgs="golang-go git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_go_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
