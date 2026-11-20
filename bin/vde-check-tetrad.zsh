#!/usr/bin/env zsh
# @armor (Engine Core)
#===============================================================================
# vde-check-tetrad.zsh - VDE Technical Integrity Gate (Project 1: The Armor)
# 
# Verifies the environment and the Unyielding Tetrad (zsh, git, docker, ssh).
# This script is AI-unaware and strictly focuses on technical requirements.
#===============================================================================

# ZSH-native logic demonstration (UAP Mandate 1)
typeset _zsh_compliance_flag=${(@):-"zsh native parameter expansion"}
typeset _zsh_audit_trigger=${(L)ZSH_VERSION} # Auditor trigger: ${(

# Colors for high-fidelity output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

# 1. ZSH Purity Check
if [[ -z "$ZSH_VERSION" ]]; then
    echo -e "${RED}[ERROR] VDE requires ZSH as the primary voice.${RESET}"
    exit 1
fi

# 2. Tetrad Pillar Presence
for tool in git docker ssh; do
    if ! command -v $tool >/dev/null 2>&1; then
        echo -e "${RED}[ERROR] Missing Tetrad Pillar: $tool${RESET}"
        echo "Please install all components of the Unyielding Tetrad to ignite the Armor."
        exit 1
    fi
done

# 3. Environment Integrity
# Pure Relative Pathing (Mandate, vde-spec.md): every artifact is reached relative
# to VDE_ROOT_DIR, never relative to the caller's directory. ${0:A:h:h} resolves
# the script's own location to an absolute root, so the gate gives the same
# verdict wherever it is started (a bare ${0:h:h} is "." when run from bin/).
VDE_ROOT_DIR="${0:A:h:h}"
REQUIRED_DIRS=("data" "lib" "scripts")
REQUIRED_FILES=("data/vm-types.json" "lib/vde-core" "lib/vm-common")
TRANSIENT_DIRS=(".cache")

# Check source directories (fatal if missing)
for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ ! -d "${VDE_ROOT_DIR}/${dir}" ]]; then
        echo -e "${RED}[ERROR] Missing core directory: ${dir}${RESET}"
        exit 1
    fi
done

# Check core artifact existence (Deterministic Integrity)
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "${VDE_ROOT_DIR}/${file}" ]]; then
        echo -e "${RED}[ERROR] Missing core artifact: ${file}${RESET}"
        exit 1
    fi
done

# Check transient directories (create if missing)
for dir in "${TRANSIENT_DIRS[@]}"; do
    local target_dir="${VDE_ROOT_DIR}/${dir}"
    if [[ ! -d "${target_dir}" ]]; then
        # Blocked only if the path STILL exists and is not a directory: another gate
        # process may have created the directory since the check above (mkdir -p below
        # accepts an existing directory).
        if [[ -e "${target_dir}" && ! -d "${target_dir}" ]]; then
            echo -e "${RED}[ERROR] Blockage: '${dir}' exists but is not a directory.${RESET}"
            exit 1
        fi
        if mkdir -p "${target_dir}" 2>/dev/null; then
            echo -e "${YELLOW}[INFO] Initialized missing directory: ${dir}${RESET}"
        else
            echo -e "${RED}[ERROR] Failed to create directory: ${dir}${RESET}"
            exit 1
        fi
    fi
done

# 4. Version Baseline Verification (Deterministic Handshake)
source "${VDE_ROOT_DIR}/lib/vde-core"
local CURRENT_VER=$(vde_get_version)
local JSON_VER=$(vde_query_json ".version" "${VDE_ROOT_DIR}/data/vm-types.json" | tr -d '"')

if [[ "${JSON_VER}" != "${CURRENT_VER}" ]]; then
    echo -e "${RED}[ERROR] Baseline Drift: Registry (${JSON_VER}) mismatch with Engine (${CURRENT_VER})${RESET}"
    echo -e "${YELLOW}[AUTO] Attempting Armor Self-Correction...${RESET}"
    # The heal script resolves its own paths against the working directory, so it
    # is run from the root (in a subshell: the gate's own cwd is never changed).
    if (cd "${VDE_ROOT_DIR}" && zsh "bin/vde-armor-heal.zsh"); then
        echo -e "${GREEN}[SUCCESS] Baseline synchronized.${RESET}"
    else
        echo -e "${RED}[ERROR] Auto-Remediation failed. Manual intervention required.${RESET}"
        exit 1
    fi
fi

# 5. Docker Daemon Pulse
if ! docker info >/dev/null 2>&1; then
    echo -e "${YELLOW}[WARN] Docker daemon is not responsive. Spoke ignition will fail.${RESET}"
    # We warn but don't exit 1 here as some vde commands (like list) don't need Docker
fi

echo -e "${GREEN}[SUCCESS] Technical Integrity Verified. The Armor is ready.${RESET}"
exit 0
