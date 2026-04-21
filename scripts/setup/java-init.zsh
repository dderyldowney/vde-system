#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Script: java
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_java_pkgs="default-jdk maven gradle git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_java_pkgs}

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
