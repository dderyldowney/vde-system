#!/usr/bin/env zsh
# VDE Phase 24 Compliance Auditor
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# Load VDE environment
VDE_ROOT_DIR="${VDE_ROOT_DIR:-$(pwd)}"
source "${VDE_ROOT_DIR}/lib/vde-constants"
source "${VDE_ROOT_DIR}/lib/vm-common"

local registry="${VDE_ROOT_DIR}/data/vm-types.conf"
local total=$(grep -c "^lang\|^service" "$registry")
local compliant=0

echo "[USP-AUDIT] Starting compliance check for $total registered VMs..."

while IFS='|' read -r _v_type _v_name _v_aliases _v_display _v_pkgs _v_custom_cmd _v_s_port _v_ssh_port; do
    # Skip comments and empty lines
    [[ "$_v_type" =~ "^(lang|service)$" ]] || continue
    
    # Extract script path (handle zsh prefix and remove /vde container prefix)
    local script_path=$(echo $_v_custom_cmd | awk '{print $NF}' | sed 's|^/vde/||')
    local script_file="${VDE_ROOT_DIR}/${script_path}"
    
    if [[ -f "$script_file" ]]; then
        local has_set_e=0
        local has_clean=0
        local has_purge=0
        
        if grep -q "set -e" "$script_file"; then has_set_e=1; fi
        if grep -q "apt-get clean" "$script_file"; then has_clean=1; fi
        if grep -q "/var/lib/apt/lists" "$script_file"; then has_purge=1; fi
        
        if [[ $has_set_e -eq 1 && $has_clean -eq 1 && $has_purge -eq 1 ]]; then
            compliant=$((compliant + 1))
        else
            echo "[FAIL] Non-compliant: $_v_name ($script_file)"
            [[ $has_set_e -eq 0 ]] && echo "  - Missing: set -e"
            [[ $has_clean -eq 0 ]] && echo "  - Missing: apt-get clean"
            [[ $has_purge -eq 0 ]] && echo "  - Missing: rm -rf /var/lib/apt/lists/*"
        fi
    else
        echo "[FAIL] Missing script: $_v_name ($script_file)"
    fi
done < "$registry"

echo "[USP-AUDIT] Phase 24 Hardening: $compliant/$total scripts compliant."

if [[ $compliant -eq $total ]]; then
    echo "[USP-SUCCESS] All spokes hardened. USP mandate satisfied."
    exit 0
else
    echo "[USP-FAILURE] Hardening verification failed."
    exit 1
fi
