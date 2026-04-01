#!/usr/bin/env zsh
#===============================================================================
# vde-enforce-uap.zsh - Universal Agent Protocol Enforcement
#
# Checks for non-ZSH shebangs in bin/ and lib/ and verifies the existence 
# of mandatory agent config files.
#===============================================================================

VDE_ROOT_DIR="${0:a:h:h}"

# Mandatory config files
MANDATORY_FILES=("AGENTS.md" "GEMINI.md" "CLAUDE.md")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

errors=0

# 1. Check for mandatory config files
for file in "${MANDATORY_FILES[@]}"; do
    if [[ ! -f "${VDE_ROOT_DIR}/${file}" ]]; then
        echo -e "${RED}[UAP-ERROR]${NC} Mandatory file missing: ${file}"
        errors=$((errors + 1))
    fi
done

# 2. Check shebangs in bin/ and lib/
check_shebangs() {
    local dir=$1
    for file in "${dir}"/*; do
        if [[ -f "${file}" ]]; then
            # Read first line
            read -r first_line < "${file}"
            # Check if it starts with #! but doesn't contain zsh
            if [[ "${first_line}" == \#!* && "${first_line}" != *zsh* ]]; then
                echo -e "${RED}[UAP-ERROR]${NC} Non-ZSH shebang found in ${file#${VDE_ROOT_DIR}/}: ${first_line}"
                errors=$((errors + 1))
            fi
        fi
    done
}

check_shebangs "${VDE_ROOT_DIR}/bin"
check_shebangs "${VDE_ROOT_DIR}/lib"

if [[ ${errors} -gt 0 ]]; then
    echo -e "${RED}[UAP-FAILURE]${NC} Protocol bypass detected (${errors} errors). VDE execution blocked."
    exit 1
fi

exit 0
