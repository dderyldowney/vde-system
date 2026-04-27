#!/usr/bin/env zsh
# @armor (Engine Core)
# Forged in Beskar: vde-certified-ghost
set -e
export DEBIAN_FRONTEND=noninteractive
source ./lib/vde-core
vde_log_info "Igniting Certified Ghost environment..."
sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*
