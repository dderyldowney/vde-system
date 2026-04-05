#!/usr/bin/env zsh
# VDE Initialization Script: flutter
# USP compliant - strictly ZSH
# Forged in Beskar

# 1. THE PACKAGE ALLOY: Define requirements with unique local prefix
local vde_flutter_pkgs="curl git unzip xz-utils zip libglu1-mesa"

# 2. THE FORGE WORK: Update and install
apt-get update
apt-get install -y ${=vde_flutter_pkgs}

# 3. CUSTOM FORGE: Setup Flutter for devuser
su devuser -c 'git clone --depth 1 https://github.com/flutter/flutter.git /home/devuser/flutter && export PATH="$PATH:/home/devuser/flutter/bin" && /home/devuser/flutter/bin/flutter precache'

# 4. PURGING THE GHOSTS: Cleanup apt artifacts
apt-get clean
rm -rf /var/lib/apt/lists/*
