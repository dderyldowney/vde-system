#!/usr/bin/env zsh
# @armor (Engine Core)
# Forged in Beskar: vde-lamp
set -e
export DEBIAN_FRONTEND=noninteractive
source ./lib/vde-core
vde_log_info "Igniting LAMP Stack environment..."
sudo apt-get update && sudo apt-get install -y php-cli mysql-client
sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*
