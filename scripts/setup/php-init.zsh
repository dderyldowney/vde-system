#!/usr/bin/env zsh
# VDE USP Hydration Script: php
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_php_pkgs="php php-cli php-xml php-mbstring php-curl composer git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_php_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
