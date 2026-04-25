#!/usr/bin/env zsh
# @forge (Self-Healer)
#===============================================================================
# vde-heal-docs.zsh - Sovereign Gospel Self-Healing Sentinel
#
# Autonomously synchronizes and updates the entire Sovereign Artifact Set.
# 1. Triggers bin/vde-sync-version for version consistency.
# 2. Updates "Date" and "Last Updated" fields across artifacts.
# 3. Synchronizes docs/available-scripts.md with bin/ contents.
#===============================================================================

# 1. Initialize the Spine
emulate -L zsh
setopt LOCAL_OPTIONS
typeset _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}
set -e

# Use relative pathing (Mandate)
source "./lib/vde-core"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[HEAL]${NC} Initiating Sovereign Self-Healing Ritual..."

# 2. Synchronize Versions (The Baseline)
echo -e "${GREEN}[HEAL]${NC} Synchronizing Version Baseline..."
zsh "./bin/vde-sync-version"

# 3. Update Dates across Sovereign Artifact Set
echo -e "${GREEN}[HEAL]${NC} Synchronizing Artifact Dates..."
CURRENT_DATE=$(date +%Y-%m-%d)
SOVEREIGN_ARTIFACTS=(
    "docs/ARCHITECTURE.md"
    "docs/TECHNICAL_DEEP_DIVE.md"
    "RELEASE_NOTES.md"
    "docs/VDE-SPEC.md"
    "USE_CASES.md"
    "VDE_ANALYSIS.md"
    "PROJECT_STATUS.md"
    "docs/SOVEREIGN_CHARTER.md"
    "docs/STDLIB.md"
)

# Portable Sed Helper
vde_sed_inplace() {
    local pattern="$1"
    local file="$2"
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' -E "${pattern}" "${file}"
    else
        sed -i -E "${pattern}" "${file}"
    fi
}

for file in "${SOVEREIGN_ARTIFACTS[@]}"; do
    if [[ -f "./${file}" ]]; then
        vde_sed_inplace "s/\*\*Date\*\*:[ ]+[0-9]{4}-[0-9]{2}-[0-9]{2}/**Date**: ${CURRENT_DATE}/" "./${file}"
        vde_sed_inplace "s/\*\*Last Updated\*\*:[ ]+[0-9]{4}-[0-9]{2}-[0-9]{2}/**Last Updated**: ${CURRENT_DATE}/" "./${file}"
        echo -e "${GREEN}[INFO]${NC} Updated date in ${file}"
    fi
done

# 4. Synchronize bin/ with available-scripts.md
echo -e "${GREEN}[HEAL]${NC} Synchronizing Script Documentation..."
AVAILABLE_SCRIPTS_DOC="./docs/available-scripts.md"

if [[ -f "${AVAILABLE_SCRIPTS_DOC}" ]]; then
    # We will identify undocumented scripts and append them to a "New/Unclassified" section
    # to maintain visibility until the Armorer manually classifies them.
    UNDOCUMENTED=()
    for script_path in "./bin"/*(N.); do
        script_name="${script_path:t}"
        [[ "${script_name}" == "."* ]] && continue
        [[ "${script_name}" == "archive" ]] && continue
        
        if ! grep -q "\`${script_name}\`" "${AVAILABLE_SCRIPTS_DOC}"; then
            UNDOCUMENTED+=("${script_name}")
        fi
    done

    if [[ ${#UNDOCUMENTED} -gt 0 ]]; then
        echo -e "${YELLOW}[WARN]${NC} Found ${#UNDOCUMENTED} undocumented scripts. Healing..."
        
        # Ensure the section exists
        if ! grep -q "## Undocumented Scripts (Pending Classification)" "${AVAILABLE_SCRIPTS_DOC}"; then
            echo -e "\n---\n\n## Undocumented Scripts (Pending Classification)\n\n| Script | Purpose |\n|--------|---------|" >> "${AVAILABLE_SCRIPTS_DOC}"
        fi
        
        for script in "${UNDOCUMENTED[@]}"; do
            # Extract first comment line as purpose
            purpose=$(grep -m1 "^# " "./bin/${script}" | sed 's/^# //' | sed 's/^@.*//' | tr -d '\r' | xargs)
            [[ -z "${purpose}" ]] && purpose="Automatically discovered - documentation pending."
            
            # Avoid duplicate appends if script was added but grep missed it due to markdown format
            if ! grep -q "| \`${script}\` |" "${AVAILABLE_SCRIPTS_DOC}"; then
                echo "| \`${script}\` | ${purpose} |" >> "${AVAILABLE_SCRIPTS_DOC}"
                echo -e "${GREEN}[INFO]${NC} Healed entry for ${script}"
            fi
        done
    fi
fi

echo -e "\n${GREEN}[HEAL-SUCCESS]${NC} Gospel has been synchronized with the physical implementation."
exit 0
