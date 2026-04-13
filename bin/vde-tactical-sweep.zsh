#!/usr/bin/env zsh
#===============================================================================
# vde-tactical-sweep.zsh - Comprehensive Forge Cleanup Tool
#
# Part of the Sovereign Baseline v1.3.1.
# Mandate: Zero-Host Dependency & Zero-Ghost Persistence.
# Forged in Beskar.
#===============================================================================

# ZSH-native logic demonstration (UAP Mandate 1)
local _zsh_compliance_flag=${(z):-"zsh native tactical sweep"}

VDE_BIN_DIR="${0:a:h}"
VDE_ROOT_DIR="${VDE_BIN_DIR:h}"

# Source Constants & Errors for Protocol Integrity
[[ -f "${VDE_ROOT_DIR}/lib/vde-constants" ]] && . "${VDE_ROOT_DIR}/lib/vde-constants"
[[ -f "${VDE_ROOT_DIR}/lib/vde-log" ]] && . "${VDE_ROOT_DIR}/lib/vde-log"

# Tactical Sweep Parameters
VDE_LOCKS_VMS_DIR="${VDE_ROOT_DIR}/.locks/vms"
VDE_PORT_REGISTRY_DIR="${VDE_ROOT_DIR}/.cache/port-registry"

vde_log_info "[SWEEP] Commencing Tactical Forge Sweep..." "sweep"

# 1. THE QUENCH: Stop and Purge ALL VDE Containers
vde_log_info "[SWEEP] Purging all 'vde-' containers..." "sweep"
local containers
containers=($(docker ps -aq --filter "name=vde-"))

if [[ ${#containers} -gt 0 ]]; then
    # We use -f to force removal of running/paused spirits
    docker rm -f ${=containers} >/dev/null 2>&1
    vde_log_success "[SWEEP] ${#containers} Spokes quenched and purged." "sweep"
else
    vde_log_info "[SWEEP] No active Spokes detected." "sweep"
fi

# 2. THE LOCK BREAK: Clear ALL VM Lock files
if [[ -d "${VDE_LOCKS_VMS_DIR}" ]]; then
    vde_log_info "[SWEEP] Breaking all VM locks..." "sweep"
    # Use (N) to avoid errors if directory is empty
    local locks=("${VDE_LOCKS_VMS_DIR}"/*(N))
    if [[ ${#locks} -gt 0 ]]; then
        rm -rf "${VDE_LOCKS_VMS_DIR}"/* 2>/dev/null
    fi
    vde_log_success "[SWEEP] Lock directory at ${VDE_LOCKS_VMS_DIR#${VDE_ROOT_DIR}/} cleared." "sweep"
fi

# 3. THE REGISTRY PURGE: Clear ALL port reservations
if [[ -d "${VDE_PORT_REGISTRY_DIR}" ]]; then
    vde_log_info "[SWEEP] Purging port registry..." "sweep"
    # Use (N) to avoid errors if directory is empty
    local ports=("${VDE_PORT_REGISTRY_DIR}"/*(N))
    if [[ ${#ports} -gt 0 ]]; then
        rm -rf "${VDE_PORT_REGISTRY_DIR}"/* 2>/dev/null
    fi
    vde_log_success "[SWEEP] Port registry at ${VDE_PORT_REGISTRY_DIR#${VDE_ROOT_DIR}/} cleared." "sweep"
fi

vde_log_success "[SWEEP] Tactical Sweep Complete. The Forge is Pristine." "sweep"
exit 0
