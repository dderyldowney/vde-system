#!/usr/bin/env zsh
# @armor (Hydration Ritual)
# Forged in Beskar: vde-lua
set -e
export DEBIAN_FRONTEND=noninteractive
source ./lib/vde-core
vde_log_info "Igniting Lua environment..."
sudo apt-get update && sudo apt-get install -y lua5.4 luarocks
sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*
