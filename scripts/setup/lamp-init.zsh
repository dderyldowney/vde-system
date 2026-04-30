#!/usr/bin/env zsh
# @armor (Engine Core)
# Forged in Beskar: vde-lamp
set -e
export DEBIAN_FRONTEND=noninteractive
source ./lib/vde-core
vde_log_info "Igniting LAMP Stack environment..."
sudo apt-get update && sudo apt-get install -y php-cli mysql-client
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
[[ -f "${VDE_ROOT_DIR}/lib/vde-core" ]] && source "${VDE_ROOT_DIR}/lib/vde-core"
vde_purge_ghosts
