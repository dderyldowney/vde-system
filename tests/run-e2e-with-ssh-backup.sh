#!/usr/bin/env zsh
# VDE E2E Test Runner with SSH Backup/Restore
# Wraps the e2e test to automatically backup/restore your SSH setup

set -e

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    BOLD=''
    RESET=''
fi

PROJECT_ROOT="$(cd "$(dirname "$0")"/../.. && pwd)"
cd "$PROJECT_ROOT"

# =============================================================================
# SSH BACKUP/RESTORE (with relative paths)
# =============================================================================

backup_ssh_setup() {
    echo ""
    echo "====================================="
    echo "Moving your personal SSH setup out of way for testing..."
    echo "==================================="
    echo ""

    # Use relative path for safety
    local ssh_dir="$HOME/.ssh"
    local temp_dir="$HOME/.ssh-vde-test-backup"

    # Create temporary directory
    mkdir -p "$temp_dir"

    # Move all SSH files (both hidden and visible)
    for file in "$ssh_dir"/.* "$ssh_dir"/*; do
        [[ -f "$file" ]] || continue
        mv "$file" "$temp_dir/" 2>/dev/null || true
    done

    echo "✓ Your SSH setup has been moved to: $temp_dir"
    if [[ -n $(ls "$temp_dir" 2>/dev/null) ]]; then
        echo "Your keys: $(ls "$temp_dir" | tr '\n' ', ')"
    fi
    echo ""
}

restore_ssh_setup() {
    echo ""
    echo "====================================="
    echo "Restoring your personal SSH setup..."
    echo "==================================="
    echo ""

    local ssh_dir="$HOME/.ssh"
    local temp_dir="$HOME/.ssh-vde-test-backup"

    if [[ ! -d "$temp_dir" ]]; then
        echo "⚠️  No backup found at: $temp_dir"
        echo "You might need to run the backup first"
        return 1
    fi

    # Move everything back
    for file in "$temp_dir"/*; do
        mv "$file" "$ssh_dir/" 2>/dev/null || true
    done

    # Remove temp dir
    rmdir "$temp_dir"  2>/dev/null || true

    echo "✓ Your SSH setup has been restored!"
    echo ""
}

# Trap to restore SSH setup even if test is interrupted
trap 'echo ""; echo ""; restore_ssh_setup; echo ""; exit 1' EXIT; exit 0

# =============================================================================
# RUN THE E2E TEST
# =============================================================================

echo -e "${BOLD}═════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}VDE E2E Test Runner (with SSH Backup/Restore)${RESET}"
echo -e "${BOLD}═════════════════════════════════════════════════════════════${RESET}"
echo ""

# Show what's about to happen
echo "This script will:"
echo "  1. Backup your personal SSH setup to ~/.ssh-vde-test-backup/"
echo "  2. Run the full end-to-end test"
echo "   3. Restore your SSH setup when done"
echo ""

echo -e "${YELLOW}⚠  Your existing VMs will NOT be touched${RESET}"
echo -e "${YELLOW}⚠  Your existing configs will NOT be modified${RESET}"
echo ""
echo -e "${BLUE}Test VMs: e2e-test-go, e2e-test-minio${RESET}"
echo ""

# Backup
backup_ssh_setup

# Run the e2e test
./tests/test-e2e-user-journey.sh "$@"

# Restore on exit or interruption
restore_ssh_setup

echo ""
echo -e "${GREEN}${BOLD}✓ E2E Test Complete!${RESET}"
echo "Your SSH setup has been restored."
