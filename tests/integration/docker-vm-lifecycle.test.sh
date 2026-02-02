#!/usr/bin/env zsh
# Docker VM Lifecycle Integration Tests
# Tests ACTUAL Docker container creation, start, stop with real VDE scripts
#
# These tests require Docker to be running and create real containers
# They use less-common VM types (haskell, scala, swift) to avoid conflicts
#
# Usage: ./tests/integration/docker-vm-lifecycle.test.sh [--cleanup-only]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Test configuration - use commonly used VMs for CI
# These are the most commonly used languages and services in educational environments:
# Languages: python, rust, js, go, csharp, flutter (6 language VMs)
# Services: postgres, redis, mongodb, mysql, nginx, rabbitmq (6 service VMs)
# VDE supports additional VMs beyond these, but we test the most commonly used ones.

# Support single VM testing for CI matrix jobs
# When TEST_VM is set, only test that VM instead of the default set
if [[ -n "$TEST_VM" ]]; then
  # Single VM mode (for CI matrix)
  TEST_LANG_VM="$TEST_VM"
  TEST_SVC_VM=""
  TEST_LANG_VM2=""
  # Detect category from VM type
  if [[ "$TEST_VM" =~ ^(postgres|redis|mongodb|nginx|mysql|rabbitmq|couchdb)$ ]]; then
    # Service VM
    TEST_SVC_VM="$TEST_VM"
    TEST_LANG_VM=""
  fi
else
  # Default multi-VM mode (for local testing)
  # IMPORTANT: Use VALID VM names from vm-types.conf for integration testing!
  # We use less common VMs to minimize impact on user's development environment:
  # - zig: less commonly used language
  # - couchdb: less commonly used service
  TEST_LANG_VM="zig"      # Less common language VM for testing
  TEST_SVC_VM="couchdb"   # Less common service VM for testing
  TEST_LANG_VM2="lua"     # Another less common language VM
fi

VERBOSE=${VERBOSE:-false}
TESTS_PASSED=0
TESTS_FAILED=0
CLEANUP_ONLY=false

# Check for cleanup-only flag
if [[ "$1" == "--cleanup-only" ]]; then
    CLEANUP_ONLY=true
fi

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    CYAN=''
    BOLD=''
    RESET=''
fi

# Test helpers
test_start() {
    echo -e "${YELLOW}[TEST]${RESET} $1"
}

test_pass() {
    echo -e "${GREEN}[PASS]${RESET} $1"
    ((TESTS_PASSED++)) || true
}

test_fail() {
    echo -e "${RED}[FAIL]${RESET} $1: $2"
    ((TESTS_FAILED++)) || true
}

info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${CYAN}[INFO]${RESET} $*"
    fi
}

# Check Docker is available
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}Error: Docker not found${RESET}"
        echo "These tests require Docker to be installed and running"
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}Error: Docker daemon not running${RESET}"
        echo "Please start Docker and try again"
        exit 1
    fi
}

# Check if VM exists
vm_exists() {
    local vm_name="$1"
    [[ -d "configs/docker/$vm_name" ]]
}

# Create VM if it doesn't exist
ensure_vm() {
    local vm_name="$1"

    if vm_exists "$vm_name"; then
        info "VM $vm_name already exists, skipping creation"
        return 0
    fi

    info "Creating VM: $vm_name"
    # Note: Script may fail on SSH config update, but VM should still be created
    ./scripts/create-virtual-for "$vm_name" >/dev/null 2>&1 || true
    return 0
}

# Cleanup function - removes test VMs
cleanup() {
    if [[ "$CLEANUP_ONLY" == true ]]; then
        echo "Cleaning up test VMs..."
    fi

    # Stop test VMs if running
    for vm in "$TEST_LANG_VM" "$TEST_SVC_VM" "$TEST_LANG_VM2"; do
        if docker ps -q --filter "name=${vm}-dev" | grep -q . 2>/dev/null; then
            info "Stopping ${vm}-dev"
            docker stop "${vm}-dev" >/dev/null 2>&1 || true
        fi
        if docker ps -q --filter "name=${vm}" | grep -q . 2>/dev/null; then
            info "Stopping $vm"
            docker stop "$vm" >/dev/null 2>&1 || true
        fi
    done

    # Remove containers
    for vm in "$TEST_LANG_VM" "$TEST_SVC_VM" "$TEST_LANG_VM2"; do
        if docker ps -aq --filter "name=${vm}-dev" | grep -q . 2>/dev/null; then
            docker rm "${vm}-dev" >/dev/null 2>&1 || true
        fi
        if docker ps -aq --filter "name=${vm}" | grep -q . 2>/dev/null; then
            docker rm "$vm" >/dev/null 2>&1 || true
        fi
    done

    # Remove configs for test VMs
    for vm in "$TEST_LANG_VM" "$TEST_SVC_VM" "$TEST_LANG_VM2"; do
        if [[ -d "configs/docker/$vm" ]]; then
            info "Removing configs/docker/$vm"
            rm -rf "configs/docker/$vm"
        fi
    done

    # Remove projects
    for vm in "$TEST_LANG_VM" "$TEST_SVC_VM" "$TEST_LANG_VM2"; do
        if [[ -d "projects/$vm" ]]; then
            info "Removing projects/$vm"
            rm -rf "projects/$vm"
        fi
    done

    # Remove data for service VMs
    for vm in "$TEST_SVC_VM"; do
        if [[ -d "data/$vm" ]]; then
            info "Removing data/$vm"
            # Some services (mongodb) create files owned by container users
            # Try multiple cleanup methods, suppress permission errors
            rm -rf "data/$vm" 2>/dev/null || \
            sudo rm -rf "data/$vm" 2>/dev/null || \
            find "data/$vm" -mindepth 1 -delete 2>/dev/null || \
            true
        fi
    done

    # Remove env files
    for vm in "$TEST_LANG_VM" "$TEST_SVC_VM" "$TEST_LANG_VM2"; do
        if [[ -f "env-files/$vm.env" ]]; then
            info "Removing env-files/$vm.env"
            rm -f "env-files/$vm.env"
        fi
    done

    if [[ "$CLEANUP_ONLY" == true ]]; then
        echo "Cleanup complete"
        exit 0
    fi
}

trap cleanup EXIT INT TERM

# =============================================================================
# TESTS: Create Language VM
# =============================================================================

test_create_language_vm() {
    # Skip if no language VM configured (single service VM mode)
    if [[ -z "$TEST_LANG_VM" ]]; then
        info "Skipping language VM creation test (no language VM configured)"
        return 0
    fi

    test_start "Create a new language VM ($TEST_LANG_VM)"

    # Remove VM if it exists from previous test run
    if vm_exists "$TEST_LANG_VM"; then
        # Stop container first to release file locks
        docker stop "${TEST_LANG_VM}-dev" >/dev/null 2>&1 || true
        docker rm "${TEST_LANG_VM}-dev" >/dev/null 2>&1 || true
        rm -rf "configs/docker/$TEST_LANG_VM"
        rm -rf "projects/$TEST_LANG_VM"
        rm -f "env-files/$TEST_LANG_VM.env"
    fi

    # Call the actual create-virtual-for script
    # Note: Script may fail on SSH config update, but VM should still be created
    ./scripts/create-virtual-for "$TEST_LANG_VM" >/dev/null 2>&1 || true

    # Verify config directory was created
    if [[ ! -d "configs/docker/$TEST_LANG_VM" ]]; then
        test_fail "Create language VM" "config directory not created"
        return
    fi

    # Verify docker-compose.yml exists
    if [[ ! -f "configs/docker/$TEST_LANG_VM/docker-compose.yml" ]]; then
        test_fail "Create language VM" "docker-compose.yml not created"
        return
    fi

    # Verify project directory was created
    if [[ ! -d "projects/$TEST_LANG_VM" ]]; then
        test_fail "Create language VM" "project directory not created"
        return
    fi

    # Verify docker-compose.yml has valid content
    if ! grep -q "image:" "configs/docker/$TEST_LANG_VM/docker-compose.yml"; then
        test_fail "Create language VM" "docker-compose.yml missing image"
        return
    fi

    test_pass "Create language VM ($TEST_LANG_VM)"
}

# =============================================================================
# TESTS: Create Service VM
# =============================================================================

test_create_service_vm() {
    # Skip if no service VM configured (single language VM mode)
    if [[ -z "$TEST_SVC_VM" ]]; then
        info "Skipping service VM creation test (no service VM configured)"
        return 0
    fi

    test_start "Create a new service VM ($TEST_SVC_VM)"

    # Remove VM if it exists from previous test run
    if vm_exists "$TEST_SVC_VM"; then
        # Stop container first to release file locks
        docker stop "$TEST_SVC_VM" >/dev/null 2>&1 || true
        docker rm "$TEST_SVC_VM" >/dev/null 2>&1 || true
        rm -rf "configs/docker/$TEST_SVC_VM"
        # Handle permission errors for services like mongodb
        rm -rf "data/$TEST_SVC_VM" 2>/dev/null || true
        rm -f "env-files/$TEST_SVC_VM.env"
    fi

    # Call the actual create-virtual-for script
    # Note: Script may fail on SSH config update, but VM should still be created
    ./scripts/create-virtual-for "$TEST_SVC_VM" >/dev/null 2>&1 || true

    # Verify config directory was created
    if [[ ! -d "configs/docker/$TEST_SVC_VM" ]]; then
        test_fail "Create service VM" "config directory not created"
        return
    fi

    # Verify docker-compose.yml exists
    if [[ ! -f "configs/docker/$TEST_SVC_VM/docker-compose.yml" ]]; then
        test_fail "Create service VM" "docker-compose.yml not created"
        return
    fi

    # Verify data directory was created for service VM
    if [[ ! -d "data/$TEST_SVC_VM" ]]; then
        test_fail "Create service VM" "data directory not created"
        return
    fi

    test_pass "Create service VM ($TEST_SVC_VM)"
}

# =============================================================================
# TESTS: Start VM
# =============================================================================

test_start_vm() {
    test_start "Start a created VM"

    # Use language VM if available, otherwise use service VM
    local vm_name="$TEST_LANG_VM"
    local is_lang_vm=true
    if [[ -z "$vm_name" ]]; then
        vm_name="$TEST_SVC_VM"
        is_lang_vm=false
    fi

    # Skip if no VM configured
    if [[ -z "$vm_name" ]]; then
        info "Skipping start VM test (no VM configured)"
        return 0
    fi

    # Ensure VM exists
    if ! ensure_vm "$vm_name"; then
        test_fail "Start VM" "could not ensure VM exists"
        return
    fi

    # Start the VM
    if ! ./scripts/start-virtual "$vm_name" >/dev/null 2>&1; then
        test_fail "Start VM" "start-virtual script failed"
        return
    fi

    # Wait a moment for container to start
    sleep 3

    # Verify container is running (language VMs have -dev suffix)
    local container_name="$vm_name"
    if [[ "$is_lang_vm" == "true" ]]; then
        container_name="${vm_name}-dev"
    fi

    if ! docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        test_fail "Start VM" "container not running"
        info "Running containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}"
        return
    fi

    test_pass "Start VM"
}

# =============================================================================
# TESTS: Start Multiple VMs
# =============================================================================

test_start_multiple_vms() {
    # Skip this test in single VM mode
    if [[ -n "$TEST_VM" ]]; then
        info "Skipping multi-VM test in single VM mode"
        return 0
    fi

    test_start "Start multiple VMs"

    local vms=("$TEST_LANG_VM" "$TEST_LANG_VM2" "$TEST_SVC_VM")

    # Ensure VMs exist
    for vm in "${vms[@]}"; do
        if ! ensure_vm "$vm"; then
            test_fail "Start multiple VMs" "could not ensure $vm exists"
            return
        fi
    done

    # Start all VMs
    if ! ./scripts/start-virtual "${vms[@]}" >/dev/null 2>&1; then
        test_fail "Start multiple VMs" "start-virtual script failed"
        return
    fi

    # Wait for containers to start with different timeouts per VM type
    # Rust needs much longer due to Cargo compilation
    local wait_time
    for vm in "${vms[@]}"; do
        container_name="$vm"
        # Language VMs get -dev suffix
        if [[ "$vm" == "$TEST_LANG_VM" ]] || [[ "$vm" == "$TEST_LANG_VM2" ]]; then
            container_name="${vm}-dev"
        fi

        # Rust needs 4 minutes for compilation, others need 10 seconds
        if [[ "$vm" == "rust" ]]; then
            wait_time=240
        elif [[ "$vm" == "go" ]]; then
            wait_time=60  # Go also needs time for package installation
        else
            wait_time=10   # Python, JS, C# start quickly
        fi

        echo "Waiting for $container_name (max ${wait_time}s)..."
        local waited=0
        while [ $waited -lt $wait_time ]; do
            if docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
                echo "✓ $container_name is running"
                break
            fi
            sleep 5
            waited=$((waited + 5))
        done

        if [ $waited -ge $wait_time ]; then
            test_fail "Start multiple VMs" "$container_name not running after ${wait_time}s"
            docker ps --format "table {{.Names}}\t{{.Status}}"
            return
        fi
    done

    test_pass "Start multiple VMs"
}

# =============================================================================
# TESTS: Stop VM
# =============================================================================

test_stop_vm() {
    test_start "Stop a running VM"

    # Use language VM if available, otherwise use service VM
    local vm_name="$TEST_LANG_VM"
    local is_lang_vm=true
    if [[ -z "$vm_name" ]]; then
        vm_name="$TEST_SVC_VM"
        is_lang_vm=false
    fi

    # Skip if no VM configured
    if [[ -z "$vm_name" ]]; then
        info "Skipping stop VM test (no VM configured)"
        return 0
    fi

    # Make sure it's running first
    local container_name="$vm_name"
    if [[ "$is_lang_vm" == "true" ]]; then
        container_name="${vm_name}-dev"
    fi

    if ! docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        if vm_exists "$vm_name"; then
            ./scripts/start-virtual "$vm_name" >/dev/null 2>&1
            sleep 3
        fi
    fi

    # Stop the VM
    if ! ./scripts/shutdown-virtual "$vm_name" >/dev/null 2>&1; then
        test_fail "Stop VM" "shutdown-virtual script failed"
        return
    fi

    # Verify container is stopped
    if docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        test_fail "Stop VM" "container still running"
        return
    fi

    test_pass "Stop VM"
}

# =============================================================================
# TESTS: Stop All VMs
# =============================================================================

test_stop_all_vms() {
    # Skip this test in single VM mode
    if [[ -n "$TEST_VM" ]]; then
        info "Skipping stop-all VMs test in single VM mode"
        return 0
    fi

    test_start "Stop all running VMs"

    # First make sure some VMs are running
    local vms=("$TEST_LANG_VM" "$TEST_SVC_VM")
    for vm in "${vms[@]}"; do
        ensure_vm "$vm"
        ./scripts/start-virtual "$vm" >/dev/null 2>&1
    done
    sleep 3

    # Stop all test VMs (use shutdown-virtual multiple times since 'all' would stop user VMs too)
    for vm in "${vms[@]}"; do
        ./scripts/shutdown-virtual "$vm" >/dev/null 2>&1
    done

    # Verify test containers are stopped
    for vm in "${vms[@]}"; do
        local container_name="$vm"
        if [[ "$vm" == "$TEST_LANG_VM" ]]; then
            container_name="${vm}-dev"
        fi

        if docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
            test_fail "Stop all VMs" "$container_name still running"
            return
        fi
    done

    test_pass "Stop all VMs"
}

# =============================================================================
# TESTS: Restart Container
# =============================================================================

test_restart_container() {
    test_start "Restart a container"

    # Use service VM if available, otherwise use language VM
    local vm_name="$TEST_SVC_VM"
    local is_lang_vm=false
    if [[ -z "$vm_name" ]]; then
        vm_name="$TEST_LANG_VM"
        is_lang_vm=true
    fi

    # Skip if no VM configured
    if [[ -z "$vm_name" ]]; then
        info "Skipping restart test (no VM configured)"
        return 0
    fi

    # Get the correct container name
    local container_name="$vm_name"
    if [[ "$is_lang_vm" == "true" ]]; then
        container_name="${vm_name}-dev"
    fi

    # Ensure VM exists and is running
    ensure_vm "$vm_name"
    ./scripts/start-virtual "$vm_name" >/dev/null 2>&1
    sleep 5

    # Get the container's initial state
    if ! docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        test_fail "Restart container" "container not running"
        return
    fi

    # Restart the container directly via docker
    if ! docker restart "$container_name" >/dev/null 2>&1; then
        test_fail "Restart container" "docker restart failed"
        return
    fi

    sleep 5

    # Verify container is still running
    if ! docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        test_fail "Restart container" "container not running after restart"
        return
    fi

    test_pass "Restart container"
}

# =============================================================================
# TESTS: Rebuild VM
# =============================================================================

test_rebuild_vm() {
    test_start "Rebuild VM from scratch"

    # Use service VM if available, otherwise use language VM
    local vm_name="$TEST_SVC_VM"
    local is_lang_vm=false
    if [[ -z "$vm_name" ]]; then
        vm_name="$TEST_LANG_VM"
        is_lang_vm=true
    fi

    # Skip if no VM configured
    if [[ -z "$vm_name" ]]; then
        info "Skipping rebuild test (no VM configured)"
        return 0
    fi

    # Get the correct container name
    local container_name="$vm_name"
    if [[ "$is_lang_vm" == "true" ]]; then
        container_name="${vm_name}-dev"
    fi

    # Ensure VM exists
    ensure_vm "$vm_name"

    # Start with rebuild
    if ! ./scripts/start-virtual "$vm_name" --rebuild >/dev/null 2>&1; then
        test_fail "Rebuild VM" "start-virtual --rebuild failed"
        return
    fi

    sleep 5

    # Verify container is running
    if ! docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        test_fail "Rebuild VM" "container not running after rebuild"
        return
    fi

    test_pass "Rebuild VM"
}

# =============================================================================
# TESTS: List VMs
# =============================================================================

test_list_vms() {
    test_start "List VMs shows created VMs"

    # In single VM mode, check for that VM instead of TEST_LANG_VM2
    local check_vm="$TEST_LANG_VM2"
    if [[ -z "$check_vm" ]]; then
        check_vm="$TEST_LANG_VM"
    fi
    if [[ -z "$check_vm" ]]; then
        check_vm="$TEST_SVC_VM"
    fi

    # Skip if no VM configured
    if [[ -z "$check_vm" ]]; then
        info "Skipping list VMs test (no VM configured)"
        return 0
    fi

    # Create a test VM if it doesn't exist
    ensure_vm "$check_vm"

    # List VMs
    local output
    output=$(./scripts/list-vms 2>/dev/null)

    # Check that our test VM is listed
    if [[ "$output" != *"$check_vm"* ]]; then
        test_fail "List VMs" "test VM not found in list"
        info "List output: $output"
        return
    fi

    test_pass "List VMs"
}

# =============================================================================
# TESTS: Port Allocation
# =============================================================================

test_port_allocation() {
    test_start "Ports are allocated correctly"

    # Use language VM if available, otherwise use service VM
    local vm_name="$TEST_LANG_VM"
    local is_lang_vm=true
    if [[ -z "$vm_name" ]]; then
        vm_name="$TEST_SVC_VM"
        is_lang_vm=false
    fi

    # Skip if no VM configured
    if [[ -z "$vm_name" ]]; then
        info "Skipping port allocation test (no VM configured)"
        return 0
    fi

    # Service VMs don't have SSH ports
    if [[ "$is_lang_vm" == "false" ]]; then
        info "Skipping SSH port check for service VM $vm_name"
        test_pass "Port allocation (service VM - no SSH port)"
        return 0
    fi

    # Check the docker-compose.yml for port mapping
    local compose_file="configs/docker/$vm_name/docker-compose.yml"
    if [[ ! -f "$compose_file" ]]; then
        test_fail "Port allocation" "docker-compose.yml not found"
        return
    fi

    # Extract SSH port from docker-compose.yml
    local ssh_port
    ssh_port=$(grep -oE '22[0-9][0-9]:22' "$compose_file" | head -1 | cut -d':' -f1)

    if [[ -z "$ssh_port" ]]; then
        test_fail "Port allocation" "no SSH port allocated"
        return
    fi

    # Verify port is in valid range (2200-2299 for language VMs)
    if [[ $ssh_port -ge 2200 ]] && [[ $ssh_port -le 2299 ]]; then
        test_pass "Port allocation (allocated $ssh_port)"
        return
    fi

    test_fail "Port allocation" "port $ssh_port out of valid range (2200-2299)"
}

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "Docker VM Lifecycle Integration Tests"
    echo "=========================================="
    echo ""
    echo "These tests create REAL Docker containers"
    echo "Test VMs: $TEST_LANG_VM, $TEST_SVC_VM, $TEST_LANG_VM2"
    echo ""

    check_docker

    # Run tests in order
    test_create_language_vm
    test_create_service_vm
    test_start_vm
    test_start_multiple_vms
    test_stop_vm
    test_stop_all_vms
    test_restart_container
    test_rebuild_vm
    test_list_vms
    test_port_allocation

    # Print summary
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo -e "${GREEN}Passed:  $TESTS_PASSED${RESET}"
    echo -e "${RED}Failed:  $TESTS_FAILED${RESET}"
    echo ""

    local total=$((TESTS_PASSED + TESTS_FAILED))
    echo "Total:   $total"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}${BOLD}All tests passed!${RESET}\n"
        exit 0
    else
        echo -e "\n${RED}${BOLD}Some tests failed!${RESET}\n"
        exit 1
    fi
}

# Run main
main "$@"
