#!/usr/bin/env zsh
# VDE Initialization Script: swift
# USP compliant - strictly ZSH
# Forged in Beskar

# 1. THE PACKAGE ALLOY: Define requirements with unique local prefix
local vde_swift_pkgs="binutils git libc6-dev curl"

# 2. THE FORGE WORK: Update and install
apt-get update
apt-get install -y ${=vde_swift_pkgs}

# 3. PURGING THE GHOSTS: Cleanup apt artifacts
apt-get clean
rm -rf /var/lib/apt/lists/*
