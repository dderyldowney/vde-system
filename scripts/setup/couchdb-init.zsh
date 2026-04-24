#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: couchdb
# Client-only hydration to satisfy matrix requirements
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_couchdb_pkgs="curl git gnupg"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_couchdb_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
