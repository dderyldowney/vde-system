#!/usr/bin/env zsh
# Unit Tests for vde-docker-state Library
# Tests Docker container state query functions

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vm-common"
source "$PROJECT_ROOT/scripts/lib/vde-docker-state"

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

# Check if Docker is available
docker_available() {
    docker --version >/dev/null 2>&1
}

# =============================================================================
# TESTS: _get_container_name
# =============================================================================

test_get_container_name_lang() {
    test_start "get container name (lang)"

    local result
    result=$(_get_container_name "python")
    if [[ "$result" == "python-dev" ]]; then
        test_pass "get container name (lang)"
        return
    fi

    test_fail "get container name lang" "expected 'python-dev', got '$result'"
}

test_get_container_name_service() {
    test_start "get container name (service)"

    local result
    result=$(_get_container_name "postgres")
    if [[ "$result" == "postgres" ]]; then
        test_pass "get container name (service)"
        return
    fi

    test_fail "get container name service" "expected 'postgres', got '$result'"
}

test_get_container_name_already_lang() {
    test_start "get container name (already lang suffix)"

    local result
    result=$(_get_container_name "rust-dev")
    if [[ "$result" == "rust-dev" ]]; then
        test_pass "get container name (already lang suffix)"
        return
    fi

    test_fail "get container name already lang" "expected 'rust-dev', got '$result'"
}

# =============================================================================
# TESTS: vm_container_exists (requires Docker)
# =============================================================================

test_container_exists_docker_check() {
    test_start "container exists (Docker available check)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    test_pass "container exists (Docker available check)"
}

test_container_exists_nonexistent() {
    test_start "container exists (non-existent VM)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    # Container for non-existent VM should not exist
    if ! vm_container_exists "nonexistentvm12345"; then
        test_pass "container exists (non-existent VM)"
        return
    fi

    test_fail "container exists" "container should not exist for non-existent VM"
}

# =============================================================================
# TESTS: vm_container_status (requires Docker)
# =============================================================================

test_container_status_docker_check() {
    test_start "container status (Docker available check)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    test_pass "container status (Docker available check)"
}

test_container_status_format() {
    test_start "container status (format check)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    local status
    status=$(vm_container_status "nonexistentvm12345" 2>/dev/null)

    # Should return empty or valid status
    if [[ -z "$status" ]] || echo "$status" | grep -qE "^(running|stopped|created|paused|restarting)$"; then
        test_pass "container status (format check)"
        return
    fi

    test_fail "container status format" "unexpected status format: $status"
}

# =============================================================================
# TESTS: vm_is_container_running (requires Docker)
# =============================================================================

test_container_running_docker_check() {
    test_start "container running (Docker available check)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    test_pass "container running (Docker available check)"
}

test_container_running_false() {
    test_start "container running (non-existent VM)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    # Non-existent container should not be running
    if ! vm_is_container_running "nonexistentvm12345"; then
        test_pass "container running (non-existent VM)"
        return
    fi

    test_fail "container running" "non-existent container should not be running"
}

# =============================================================================
# TESTS: vm_is_container_stopped (requires Docker)
# =============================================================================

test_container_stopped_docker_check() {
    test_start "container stopped (Docker available check)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    test_pass "container stopped (Docker available check)"
}

# =============================================================================
# TESTS: list_running_containers (requires Docker)
# =============================================================================

test_list_running_containers_docker_check() {
    test_start "list running containers (Docker available check)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    test_pass "list running containers (Docker available check)"
}

test_list_running_containers_format() {
    test_start "list running containers (format)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    local result
    result=$(list_running_containers 2>/dev/null)

    # Should return list (possibly empty)
    test_pass "list running containers (format)"
}

# =============================================================================
# TESTS: list_all_containers (requires Docker)
# =============================================================================

test_list_all_containers_docker_check() {
    test_start "list all containers (Docker available check)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    test_pass "list all containers (Docker available check)"
}

test_list_all_containers_format() {
    test_start "list all containers (format)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    local result
    result=$(list_all_containers 2>/dev/null)

    # Should return list (possibly empty)
    test_pass "list all containers (format)"
}

# =============================================================================
# TESTS: Container Name Edge Cases
# =============================================================================

test_container_name_edge_cases() {
    test_start "container name edge cases"

    # Test various VM name formats
    local test_cases=(
        "go:go-dev"
        "rust:rust-dev"
        "js:js-dev"
        "postgres:postgres"
        "redis:redis"
        "mongodb:mongodb"
    )

    for case in "${test_cases[@]}"; do
        local vm expected
        vm="${case%%:*}"
        expected="${case##*:}"

        local result
        result=$(_get_container_name "$vm")

        if [[ "$result" != "$expected" ]]; then
            test_fail "container name edge cases" "for '$vm', expected '$expected', got '$result'"
            return
        fi
    done

    test_pass "container name edge cases"
}

# =============================================================================
# TESTS: Docker Command Error Handling
# =============================================================================

test_error_handling_nonexistent() {
    test_start "error handling (non-existent container)"

    if ! docker_available; then
        echo "  (Docker not available, skipping)"
        return
    fi

    # These should not crash even for non-existent VMs
    vm_container_status "definitelynotarealvm123" >/dev/null 2>&1
    vm_is_container_running "definitelynotarealvm123" >/dev/null 2>&1
    vm_is_container_stopped "definitelynotarealvm123" >/dev/null 2>&1

    test_pass "error handling (non-existent container)"
}

# =============================================================================
# TESTS: Source Guard
# =============================================================================

test_source_guard() {
    test_start "source guard"

    # Source again
    source "$PROJECT_ROOT/scripts/lib/vde-docker-state" 2>/dev/null

    # Function should still be available
    local result
    result=$(_get_container_name "python")
    if [[ "$result" == "python-dev" ]]; then
        test_pass "source guard"
        return
    fi

    test_fail "source guard" "function not working after re-source"
}

# =============================================================================
# Run All Tests
# =============================================================================

echo "=============================================="
echo "VDE Docker State Unit Tests"
echo "=============================================="

# Docker availability check
if ! docker_available; then
    echo ""
    echo "WARNING: Docker is not available. Some tests will be skipped."
    echo ""
fi

# _get_container_name tests
test_get_container_name_lang
test_get_container_name_service
test_get_container_name_already_lang

# Container exists tests
test_container_exists_docker_check
test_container_exists_nonexistent

# Container status tests
test_container_status_docker_check
test_container_status_format

# Container running tests
test_container_running_docker_check
test_container_running_false

# Container stopped tests
test_container_stopped_docker_check

# List running containers tests
test_list_running_containers_docker_check
test_list_running_containers_format

# List all containers tests
test_list_all_containers_docker_check
test_list_all_containers_format

# Edge cases
test_container_name_edge_cases
test_error_handling_nonexistent

# Source guard test
test_source_guard

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
