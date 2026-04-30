#!/usr/bin/env zsh
# @armor (Engine Core)
# Forged in Beskar: vde-mean
set -e
export DEBIAN_FRONTEND=noninteractive
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
[[ -f "${VDE_ROOT_DIR}/lib/vde-core" ]] && source "${VDE_ROOT_DIR}/lib/vde-core"
[[ -f "${VDE_ROOT_DIR}/lib/vde-log" ]] && source "${VDE_ROOT_DIR}/lib/vde-log"

vde_log_info "Igniting MEAN Stack environment..."
sudo apt-get update && sudo apt-get install -y mongodb-clients

# PURGING THE GHOSTS (Rule 12.5)
vde_purge_ghosts
