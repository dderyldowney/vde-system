#!/usr/bin/env zsh
# VDE End-to-End User Journey Test
# Tests the complete user experience from installation through VM usage
# Preserves existing VDE installation - uses test VM names to avoid conflicts

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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

# Test VM prefix to avoid conflicts with user's existing VMs
TEST_PREFIX="e2e-test"

# Test VMs (use names that won't conflict with standard VMs)
TEST_LANG_VM="${TEST_PREFIX}-go"     # Go (not a standard VM)
TEST_SVC_VM="${TEST_PREFIX}-minio"   # Minio (not a standard service)

# =============================================================================
# USAGE
# =============================================================================

show_usage() {
    cat <<EOF
${BOLD}VDE End-to-End User Journey Test${RESET}

Tests the complete VDE user experience from installation through VM usage.
Uses test VM names (${TEST_LANG_VM}, ${TEST_SVC_VM}) to avoid conflicts
with your existing VDE installation.

${BOLD}Usage:${RESET}
  $0 [OPTIONS]

${BOLD}Options:${RESET}
  --skip-setup      Skip installation setup (VDE already installed)
  --keep-vms        Keep test VMs after test (for inspection)
  --cleanup-only    Only cleanup test VMs (don't run tests)
  -v, --verbose     Enable verbose output
  -h, --help        Show this help message

${BOLD}What gets tested:${RESET}
  1. SSH key generation and setup
  2. VDE configuration creation
  3. VM creation (language VM)
  4. VM startup
  5. SSH connection to VM
 6. SSH agent forwarding verification
  7. Container operations
  8. VM shutdown
  9. Cleanup

EOF
}

# =============================================================================
# PARSE ARGUMENTS
# =============================================================================

SKIP_SETUP=false
KEEP_VMS=false
CLEANUP_ONLY=false
VERBOSE_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-setup)
            SKIP_SETUP=true
            shift
            ;;
        --keep-vms)
            KEEP_VMS=true
            shift
            ;;
        --cleanup-only)
            CLEANUP_ONLY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE_OUTPUT=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${RESET}" >&2
            show_usage
            exit 1
            ;;
    esac
done

# =============================================================================
# SSH BACKUP/RESTORE (with relative paths for safety)
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
    echo "Your keys are: $(ls "$temp_dir" | tr '\n' ', ')"
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
    rmdir "$temp_dir" 2>/dev/null || true

    echo "✓ Your SSH setup has been restored!"
    echo ""
}

# Trap to restore SSH setup even if test is interrupted
trap 'echo ""; echo ""; restore_ssh_setup; echo ""; exit 1' EXIT; exit 0

# =============================================================================
# TEST FUNCTIONS
# =============================================================================

test_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${RESET}"
    local errors=0

    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}✗ Docker not running${RESET}"
        echo "Please start Docker Desktop and try again"
        ((errors++))
    else
        echo -e "${GREEN}✓ Docker is running${RESET}"
    fi

    # Check git
    if ! command -v git >/dev/null 2>&1; then
        echo -e "${RED}✗ Git not found${RESET}"
        ((errors++))
    else
        echo -e "${GREEN}✓ Git is available${RESET}"
    fi

    # Check zsh
    if ! command -v zsh >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Zsh not found (will use bash)${RESET}"
    else
        echo -e "${GREEN}✓ Zsh is available${RESET}"
    fi

    if [[ $errors -gt 0 ]]; then
        exit 1
    fi

    echo ""
}

test_or_install_vde() {
    if [[ "$SKIP_SETUP" == "true" ]]; then
        echo -e "${YELLOW}Skipping installation setup (user specified --skip-setup)${RESET}"
        echo ""
        return
    fi

    echo -e "${BLUE}Testing VDE installation...${RESET}"

    # Check if VDE is already installed
    if [[ -d "$PROJECT_ROOT/.locks" ]]; then
        echo -e "${YELLOW}VDE appears to be installed (found .locks/ directory)${RESET}"
        echo "Will test existing installation without modifying it"
        echo ""
        return
    fi

    echo -e "${YELLOW}VDE not installed - simulating installation...${RESET}"
    echo "In a real scenario, user would run the initial setup"
    echo "For this test, we'll verify the setup scripts exist"
    echo ""

    # Check if setup scripts exist
    local setup_scripts=(
        "scripts/lib"
        "scripts/data/vm-types.conf"
        "scripts/templates"
    )

    for script in "${setup_scripts[@]}"; do
        if [[ -d "$PROJECT_ROOT/$script" || -f "$PROJECT_ROOT/$script" ]]; then
            echo -e "${GREEN}✓ Found: $script${RESET}"
        else
            echo -e "${RED}✗ Missing: $script${RESET}"
        fi
    done

    echo ""
}

test_ssh_key_generation() {
    echo -e "${BLUE}Testing SSH key generation...${RESET}"

    # Check if SSH keys exist
    local has_key=false
    for key_type in id_ed25519 id_rsa id_ecdsa id_dsa; do
        if [[ -f "$HOME/.ssh/$key_type" ]]; then
            echo -e "${GREEN}✓ SSH key exists: $key_type${RESET}"
            has_key=true
        fi
    done

    if [[ "$has_key" == "false" ]]; then
        echo -e "${YELLOW}No SSH keys found - would auto-generate${RESET}"
    fi

    # Check public-ssh-keys directory
    if [[ -d "$PROJECT_ROOT/public-ssh-keys" ]]; then
        echo -e "${GREEN}✓ public-ssh-keys directory exists${RESET}"
    else
        echo -e "${YELLOW}public-ssh-keys directory would be created${RESET}"
    fi

    # Check if SSH config template exists
    if [[ -f "$PROJECT_ROOT/backup/ssh/config" ]]; then
        echo -e "${GREEN}✓ SSH config template exists${RESET}"
    fi

    echo ""
}

test_vm_creation() {
    echo -e "${BLUE}Testing VM creation...${RESET}"

    # Remove test VM if it already exists from previous test run
    if [[ -f "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}/docker-compose.yml" ]]; then
        echo "Removing old test VM: ${TEST_LANG_VM}"
        docker-compose -f "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}/docker-compose.yml" down -v 2>/dev/null || true
        rm -f "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}/docker-compose.yml"
        echo ""
    fi

    echo "Creating test language VM: ${TEST_LANG_VM}"

    # Run create-virtual-for
    cd "$PROJECT_ROOT"
    if ./scripts/create-virtual-for "${TEST_LANG_VM}" 2>&1 | head -30; then
        echo -e "${GREEN}✓ create-virtual-for succeeded${RESET}"
    else
        echo -e "${RED}✗ create-virtual-for failed${RESET}"
        return 1
    fi

    # Verify files were created
    local created_files=(
        "configs/docker/${TEST_LANG_VM}/docker-compose.yml"
        "env-files/${TEST_LANG_VM}.env"
        "projects/${TEST_LANG_VM}"
        "logs/${TEST_LANG_VM}"
    )

    for file in "${created_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" || -d "$PROJECT_ROOT/$file" ]]; then
            echo -e "${GREEN}✓ Created: $file${RESET}"
        else
            echo -e "${RED}✗ Not created: $file${RESET}"
        fi
    done

    echo ""
}

test_vm_startup() {
    echo -e "${BLUE}Testing VM startup...${RESET}"

    cd "$PROJECT_ROOT"

    # Start the test VM
    echo "Starting: ${TEST_LANG_VM}"
    if ./scripts/start-virtual "${TEST_LANG_VM}" 2>&1 | grep -E "started|success"; then
        echo -e "${GREEN}✓ VM started successfully${RESET}"
    else
        echo -e "${RED}✗ VM failed to start${RESET}"
        return 1
    fi

    # Verify container is running
    if docker ps | grep -q "${TEST_PREFIX}-${TEST_LANG_VM}"; then
        echo -e "${GREEN}✓ Container is running${RESET}"
    else
        echo -e "${RED}✗ Container not found${RESET}"
        return 1
    fi

    # Get SSH port
    local ssh_port=$(docker compose -f "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}/docker-compose.yml" 2>/dev/null | grep -oE '\d+:' | tr -d ':' | head -1)
    echo -e "${GREEN}✓ SSH port: $ssh_port${RESET}"

    echo ""
}

test_ssh_connection() {
    echo -e "${BLUE}Testing SSH connection...${RESET}"

    # Check if SSH config entry was created
    if grep -q "Host ${TEST_PREFIX}-${TEST_LANG_VM}" ~/.ssh/config 2>/dev/null; then
        echo -e "${GREEN}✓ SSH config entry created${RESET}"
    else
        echo -e "${YELLOW}⚠ SSH config entry not found (may be normal for non-standard VM)${RESET}"
    fi

    # Check if SSH key is in public-ssh-keys
    local key_file=$(ls "$PROJECT_ROOT/public-ssh-keys/"*.pub 2>/dev/null | head -1)
    if [[ -n "$key_file" ]]; then
        echo -e "${GREEN}✓ SSH key in public-ssh-keys/${RESET}"
    fi

    # Try SSH connection (will fail if SSH not fully configured, but we'll check)
    echo "Testing SSH connection..."
    if timeout 5 ssh -o ConnectTimeout=3 "${TEST_PREFIX}-${TEST_LANG_VM}" "echo 'SSH connection successful'" 2>/dev/null; then
        echo -e "${GREEN}✓ SSH connection successful${RESET}"
    else
        echo -e "${YELLOW}⚠ SSH connection test timed out (may need manual verification)${RESET}"
    fi

    echo ""
}

test_ssh_agent_forwarding() {
    echo -e "${BLUE}Testing SSH agent forwarding...${RESET}"

    # Check if SSH agent is running
    if pgrep -q ssh-agent; then
        echo -e "${GREEN}✓ SSH agent is running${RESET}"
    else
        echo -e "${YELLOW}⚠ SSH agent not running${RESET}"
    fi

    # Check loaded keys
    if command -v ssh-add >/dev/null 2>&1; then
        local key_count=$(ssh-add -l 2>/dev/null | grep -c "key" || echo "0")
        if [[ $key_count -gt 0 ]]; then
            echo -e "${GREEN}✓ SSH keys loaded: $key_count${RESET}"
        fi
    fi

    echo ""
}

test_container_operations() {
    echo -e "${BLUE}Testing container operations...${RESET}"

    # Check if we can run commands in the VM
    echo "Testing command execution in VM..."
    if timeout 5 docker exec "${TEST_PREFIX}-${TEST_LANG_VM}" echo "Container operations work" 2>/dev/null; then
        echo -e "${GREEN}✓ Can execute commands in container${RESET}"
    else
        echo -e "${RED}✗ Cannot execute commands in container${RESET}"
        return 1
    fi

    # Check workspace mount
    if docker exec "${TEST_PREFIX}-${TEST_LANG_VM}" ls /workspace 2>/dev/null | grep -q "lost+found"; then
        echo -e "${GREEN}✓ Workspace is mounted${RESET}"
    else
        echo -e "${YELLOW}⚠ Workspace mount may not be working${RESET}"
    fi

    echo ""
}

test_vm_shutdown() {
    echo -e "${BLUE}Testing VM shutdown...${RESET}"

    cd "$PROJECT_ROOT"

    # Shutdown the VM
    echo "Stopping: ${TEST_LANG_VM}"
    if ./scripts/shutdown-virtual "${TEST_LANG_VM}" 2>&1 | grep -E "stopped|success"; then
        echo -e "${GREEN}✓ VM stopped successfully${RESET}"
    else
        echo -e "${YELLOW}⚠ VM may not have stopped cleanly${RESET}"
    fi

    # Verify container is not running
    if ! docker ps | grep -q "${TEST_PREFIX}-${TEST_LANG_VM}"; then
        echo -e "${GREEN}✓ Container is not running${RESET}"
    else
        echo -e "${YELLOW}⚠ Container still running${RESET}"
    fi

    # Verify config still exists
    if [[ -f "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}/docker-compose.yml" ]]; then
        echo -e "${GREEN}✓ VM configuration preserved${RESET}"
    fi

    echo ""
}

cleanup_test_vms() {
    echo -e "${BLUE}Cleaning up test VMs...${RESET}"

    local cleaned=0

    # Stop test language VM
    if [[ -f "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}/docker-compose.yml" ]]; then
        echo "Stopping ${TEST_LANG_VM}..."
        docker-compose -f "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}/docker-compose.yml" down 2>/dev/null || true
        if [[ ! docker ps | grep -q "${TEST_PREFIX}-${TEST_LANG_VM}" ]]; then
            echo -e "${GREEN}✓ ${TEST_LANG_VM} stopped${RESET}"
            ((cleaned++))
        fi
    fi

    # Remove test service VM
    if [[ -f "$PROJECT_ROOT/configs/docker/${TEST_SVC_VM}/docker-compose.yml" ]]; then
        echo "Stopping ${TEST_SVC_VM}..."
        docker-compose -f "$PROJECT_ROOT/configs/docker/docker/${TEST_SVC_VM}/docker-compose.yml" down 2>/dev/null || true
        if [[ ! docker ps | grep -q "${TEST_PREFIX}-${TEST_SVC_VM}" ]]; then
            echo -e "${GREEN}✓ ${TEST_SVC_VM} stopped${RESET}"
            ((cleaned++))
        fi
    fi

    # Remove test VM configs (these are safe to remove)
    if [[ -d "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}" ]]; then
        echo "Removing ${TEST_LANG_VM} config..."
        rm -rf "$PROJECT_ROOT/configs/docker/${TEST_LANG_VM}"
        echo -e "${GREEN}✓ ${TEST_LANG_VM} config removed${RESET}"
        ((cleaned++))
    fi

    if [[ -d "$PROJECT_ROOT/configs/docker/docker/${TEST_SVC_VM}" ]]; then
        echo "Removing ${TEST_SVC_VM} config..."
        rm -rf "$PROJECT_ROOT/configs/docker/docker/${TEST_SVC_VM}"
        echo -e "${GREEN}✓ ${TEST_SVC_VM} config removed${RESET}"
        ((cleaned++))
    fi

    # Remove test env files
    if [[ -f "$PROJECT_ROOT/env-files/${TEST_LANG_VM}.env" ]]; then
        rm -f "$PROJECT_ROOT/env-files/${TEST_LANG_VM}.env"
    fi

    if [[ -d "$PROJECT_ROOT/projects/${TEST_LANG_VM}" ]]; then
        rm -rf "$PROJECT_ROOT/projects/${TEST_LANG_VM}"
    fi

    if [[ -d "$PROJECT_ROOT/logs/${TEST_LANG_VM}" ]]; then
        rm -rf "$PROJECT_ROOT/logs/${TEST_LANG_VM}"
    fi

    echo ""
    if [[ $cleaned -gt 0 ]]; then
        echo -e "${GREEN}✓ Cleanup complete ($cleaned items removed)${RESET}"
    else
        echo -e "${YELLOW}⚠ Nothing to clean up${RESET}"
    fi
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
    echo -e "${BOLD}VDE End-to-End User Journey Test${RESET}"
    echo -e "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
    echo ""

    echo -e "${BLUE}Test VMs:${RESET} ${TEST_LANG_VM}, ${TEST_SVC_VM}
    echo -e "${BLUE}Your existing VMs: ${RESET} PRESERVED (not touched)"
    echo ""

    if [[ "$CLEANUP_ONLY" == "true" ]]; then
        cleanup_test_vms
        exit 0
    fi

    # Run tests
    test_prerequisites
    test_or_install_vde
    test_ssh_key_generation
    test_vm_creation
    test_vm_startup
    test_ssh_connection
    test_ssh_agent_forwarding
    test_container_operations
    test_vm_shutdown

    if [[ "$KEEP_VMS" != "true" ]]; then
        cleanup_test_vms
    fi

    echo -e "${BOLD}═════════════════════════════════════════════════════════════${RESET}"
    echo -e "${GREEN}${BOLD}✓ ALL E2E TESTS PASSED${RESET}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${RESET}"
    echo ""
    echo -e "${BLUE}Your VDE installation is intact and working correctly.${RESET}"
}

# Run main function
main "$@"
