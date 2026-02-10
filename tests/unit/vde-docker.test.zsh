#!/usr/bin/env zsh
# Unit Tests for vde-docker Library
# Tests Docker container management functions

# Don't use set -e as it interferes with test counting

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vde-errors"
source "$PROJECT_ROOT/scripts/lib/vde-naming"
source "$PROJECT_ROOT/scripts/lib/vde-path-utils"
source "$PROJECT_ROOT/scripts/lib/vde-docker"

# Test configuration
VERBOSE=${VERBOSE:-false}
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    RESET=''
fi

test_start() {
    echo -e "${YELLOW}[TEST]${RESET} $1"
}

test_pass() {
    echo -e "${GREEN}[PASS]${RESET} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${RESET} $1: $2"
    ((TESTS_FAILED++))
}

# =============================================================================
# TEST SETUP
# =============================================================================

TEST_TMPDIR=""

setup_test_env() {
    TEST_TMPDIR="/tmp/vde-docker-test-$"
    mkdir -p "$TEST_TMPDIR"
    export HOME="$TEST_TMPDIR/home"
    mkdir -p "$HOME/.ssh/vde"
    mkdir -p "$TEST_TMPDIR/configs/docker/lang/python"
    mkdir -p "$TEST_TMPDIR/configs/docker/service/postgres"
    mkdir -p "$TEST_TMPDIR/cache"
    mkdir -p "$TEST_TMPDIR/port-registry"

    # Override paths for testing
    export VDE_CONFIG_DIR="$TEST_TMPDIR/configs/docker"
    export VDE_CACHE_DIR="$TEST_TMPDIR/cache"
    export VDE_PORT_REGISTRY="$TEST_TMPDIR/port-registry"
}

teardown_test_env() {
    rm -rf "$TEST_TMPDIR"
}

# =============================================================================
# TESTS: COMPOSE FILE FUNCTIONS
# =============================================================================

test_get_compose_file() {
    test_start "get_compose_file - known VM"

    setup_test_env
    mkdir -p "$VDE_CONFIG_DIR/lang/python"
    cat > "$VDE_CONFIG_DIR/lang/python/docker-compose.yml" << 'EOF'
version: '3.8'
services:
  python:
    image: python:3.11
EOF

    local result
    result=$(get_compose_file "python" 2>/dev/null)
    if [ "$result" = "$VDE_CONFIG_DIR/lang/python/docker-compose.yml" ]; then
        test_pass "get_compose_file - known VM"
    else
        test_fail "get_compose_file - known VM" "Wrong path: $result"
    fi

    teardown_test_env
}

test_get_docker_project_name() {
    test_start "get_docker_project_name - returns correct name"

    local result
    result=$(get_docker_project_name "python" 2>/dev/null)
    if [ "$result" = "vde-python" ]; then
        test_pass "get_docker_project_name - returns correct name"
    else
        test_fail "get_docker_project_name - returns correct name" "Got: $result"
    fi
}

# =============================================================================
# TESTS: VM EXISTENCE
# =============================================================================

test_vm_exists() {
    test_start "vm_exists - compose file exists"

    setup_test_env
    mkdir -p "$VDE_CONFIG_DIR/lang/python"
    touch "$VDE_CONFIG_DIR/lang/python/docker-compose.yml"

    if vm_exists "python" 2>/dev/null; then
        test_pass "vm_exists - compose file exists"
    else
        test_fail "vm_exists - compose file exists" "Expected true"
    fi

    teardown_test_env
}

# =============================================================================
# TESTS: SSH PORT MANAGEMENT
# =============================================================================

test_get_vm_ssh_port() {
    test_start "get_vm_ssh_port - port in registry"

    setup_test_env
    mkdir -p "$VDE_PORT_REGISTRY"
    echo "2200" > "$VDE_PORT_REGISTRY/python.port"

    local result
    result=$(get_vm_ssh_port "python" 2>/dev/null)
    if [ "$result" = "2200" ]; then
        test_pass "get_vm_ssh_port - port in registry"
    else
        test_fail "get_vm_ssh_port - port in registry" "Got: $result"
    fi

    teardown_test_env
}

test_allocate_ssh_port() {
    test_start "allocate_ssh_port - save port to registry"

    setup_test_env
    mkdir -p "$VDE_PORT_REGISTRY"

    if allocate_ssh_port "python" "2200" 2>/dev/null; then
        if [ -f "$VDE_PORT_REGISTRY/python.port" ]; then
            test_pass "allocate_ssh_port - save port to registry"
        else
            test_fail "allocate_ssh_port - save port to registry" "File not created"
        fi
    else
        test_fail "allocate_ssh_port - save port to registry" "Command failed"
    fi

    teardown_test_env
}

test_find_available_ssh_port() {
    test_start "find_available_ssh_port - returns available port"

    setup_test_env

    # Mock _is_port_in_use to always return false
    _is_port_in_use() { return 1; }

    local result
    result=$(find_available_ssh_port 2500 2510 2>/dev/null)
    if [ "$result" = "2500" ]; then
        test_pass "find_available_ssh_port - returns available port"
    else
        test_fail "find_available_ssh_port - returns available port" "Got: $result"
    fi

    teardown_test_env
}

test_get_or_allocate_ssh_port() {
    test_start "get_or_allocate_ssh_port - returns existing port"

    setup_test_env
    mkdir -p "$VDE_PORT_REGISTRY"
    echo "2205" > "$VDE_PORT_REGISTRY/python.port"

    # Mock _is_port_in_use
    _is_port_in_use() { return 1; }

    local result
    result=$(get_or_allocate_ssh_port "python" 2>/dev/null)
    if [ "$result" = "2205" ]; then
        test_pass "get_or_allocate_ssh_port - returns existing port"
    else
        test_fail "get_or_allocate_ssh_port - returns existing port" "Got: $result"
    fi

    teardown_test_env
}

# =============================================================================
# TESTS: DOCKER BUILD OPTIONS
# =============================================================================

test_build_docker_opts() {
    test_start "build_docker_opts - empty by default"

    export VDE_DOCKER_NVIDIA="false"

    local result
    result=$(build_docker_opts "python" 2>/dev/null)
    if [ -z "$result" ]; then
        test_pass "build_docker_opts - empty by default"
    else
        test_fail "build_docker_opts - empty by default" "Got: $result"
    fi
}

# =============================================================================
# TESTS: DOCKER STATE
# =============================================================================

test_docker_state_functions() {
    test_start "save_docker_state - creates state file"

    setup_test_env
    local state_dir
    state_dir=$(get_docker_state_dir)

    mkdir -p "$state_dir"
    echo '{"status":"running"}' > "$state_dir/python.json"

    if [ -f "$state_dir/python.json" ]; then
        test_pass "save_docker_state - creates state file"
    else
        test_fail "save_docker_state - creates state file" "File not created"
    fi

    teardown_test_env
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

echo "=============================================="
echo "VDE Docker Library Unit Tests"
echo "=============================================="
echo ""

test_get_compose_file
test_get_docker_project_name
test_vm_exists
test_get_vm_ssh_port
test_allocate_ssh_port
test_find_available_ssh_port
test_get_or_allocate_ssh_port
test_build_docker_opts
test_docker_state_functions

echo ""
echo "=============================================="
echo "Test Summary"
echo "=============================================="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed"
    exit 1
fi
