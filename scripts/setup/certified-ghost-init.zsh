#!/usr/bin/env zsh
# @armor (Engine Core)
# Forged in Beskar: vde-certified-ghost
set -e
export DEBIAN_FRONTEND=noninteractive
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
[[ -f "${VDE_ROOT_DIR}/lib/vde-core" ]] && source "${VDE_ROOT_DIR}/lib/vde-core"
vde_log_info "Igniting Certified Ghost environment..."
# PURGING THE GHOSTS (Rule 12.5)
vde_purge_ghosts
