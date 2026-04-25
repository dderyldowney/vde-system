#!/usr/bin/env zsh
# @armor (Hydration Ritual)
# Forged in Beskar: vde-mean
set -e
export DEBIAN_FRONTEND=noninteractive
source ./lib/vde-core
vde_log_info "Igniting MEAN Stack environment..."
sudo apt-get update && sudo apt-get install -y mongodb-clients
sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*
