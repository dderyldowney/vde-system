#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Script: testport2
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive

# 2. THE FORGE WORK (top is already in base)
apt-get update

# 3. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
