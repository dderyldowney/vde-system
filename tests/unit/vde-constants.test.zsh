#!/usr/bin/env zsh
# Unit Tests for vde-constants Library
# Tests all constant values and configurations

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/scripts/lib/vde-constants"

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
# TESTS: Return Codes
# =============================================================================

test_return_codes_exist() {
    test_start "return codes exist"

    if [[ -n "$VDE_SUCCESS" ]] && \
       [[ -n "$VDE_ERR_GENERAL" ]] && \
       [[ -n "$VDE_ERR_INVALID_INPUT" ]] && \
       [[ -n "$VDE_ERR_NOT_FOUND" ]] && \
       [[ -n "$VDE_ERR_PERMISSION" ]] && \
       [[ -n "$VDE_ERR_TIMEOUT" ]] && \
       [[ -n "$VDE_ERR_EXISTS" ]] && \
       [[ -n "$VDE_ERR_DEPENDENCY" ]] && \
       [[ -n "$VDE_ERR_DOCKER" ]] && \
       [[ -n "$VDE_ERR_LOCK" ]]; then
        test_pass "return codes exist"
        return
    fi

    test_fail "return codes exist" "some return codes are missing"
}

test_return_codes_values() {
    test_start "return codes values"

    if [[ "$VDE_SUCCESS" -eq 0 ]] && \
       [[ "$VDE_ERR_GENERAL" -eq 1 ]] && \
       [[ "$VDE_ERR_INVALID_INPUT" -eq 2 ]] && \
       [[ "$VDE_ERR_NOT_FOUND" -eq 3 ]] && \
       [[ "$VDE_ERR_PERMISSION" -eq 4 ]] && \
       [[ "$VDE_ERR_TIMEOUT" -eq 5 ]] && \
       [[ "$VDE_ERR_EXISTS" -eq 6 ]] && \
       [[ "$VDE_ERR_DEPENDENCY" -eq 7 ]] && \
       [[ "$VDE_ERR_DOCKER" -eq 8 ]] && \
       [[ "$VDE_ERR_LOCK" -eq 9 ]]; then
        test_pass "return codes values"
        return
    fi

    test_fail "return codes values" "return codes have incorrect values"
}

# =============================================================================
# TESTS: Port Configuration
# =============================================================================

test_port_ranges_exist() {
    test_start "port ranges exist"

    if [[ -n "$VDE_LANG_PORT_START" ]] && \
       [[ -n "$VDE_LANG_PORT_END" ]] && \
       [[ -n "$VDE_SVC_PORT_START" ]] && \
       [[ -n "$VDE_SVC_PORT_END" ]]; then
        test_pass "port ranges exist"
        return
    fi

    test_fail "port ranges exist" "some port range constants are missing"
}

test_port_ranges_values() {
    test_start "port ranges values"

    if [[ "$VDE_LANG_PORT_START" -eq 2200 ]] && \
       [[ "$VDE_LANG_PORT_END" -eq 2299 ]] && \
       [[ "$VDE_SVC_PORT_START" -eq 2400 ]] && \
       [[ "$VDE_SVC_PORT_END" -eq 2499 ]]; then
        test_pass "port ranges values"
        return
    fi

    test_fail "port ranges values" "port ranges have incorrect values"
}

test_container_ssh_port() {
    test_start "container SSH port"

    if [[ "$VDE_CONTAINER_SSH_PORT" -eq 22 ]]; then
        test_pass "container SSH port"
        return
    fi

    test_fail "container SSH port" "expected 22, got $VDE_CONTAINER_SSH_PORT"
}

# =============================================================================
# TESTS: Docker Configuration
# =============================================================================

test_docker_config_exist() {
    test_start "docker config exist"

    if [[ -v VDE_DOCKER_NETWORK ]] && \
       [[ -v VDE_COMPOSE_PROJECT_PREFIX ]] && \
       [[ -v VDE_CONTAINER_PREFIX ]]; then
        test_pass "docker config exist"
        return
    fi

    test_fail "docker config exist" "some docker constants are missing"
}

test_container_prefix() {
    test_start "container prefix"

    if [[ "$VDE_CONTAINER_PREFIX" == "vde-" ]]; then
        test_pass "container prefix"
        return
    fi

    test_fail "container prefix" "expected 'vde-', got '$VDE_CONTAINER_PREFIX'"
}

# =============================================================================
# TESTS: SSH Isolation Configuration
# =============================================================================

test_ssh_isolation_exist() {
    test_start "SSH isolation config exist"

    if [[ -n "$VDE_HOME_DIR" ]] && \
       [[ -n "$VDE_SSH_DIR" ]] && \
       [[ -n "$VDE_SSH_CONFIG" ]] && \
       [[ -n "$VDE_SSH_KNOWN_HOSTS" ]] && \
       [[ -n "$VDE_SSH_IDENTITY" ]] && \
       [[ -n "$VDE_SSH_IDENTITY_PUB" ]]; then
        test_pass "SSH isolation config exist"
        return
    fi

    test_fail "SSH isolation config exist" "some SSH isolation constants are missing"
}

test_ssh_paths_under_home() {
    test_start "SSH paths are under HOME"

    if [[ "$VDE_SSH_DIR" == "$HOME/.ssh/vde" ]]; then
        test_pass "SSH paths are under HOME"
        return
    fi

    test_fail "SSH paths" "VDE_SSH_DIR should be under HOME"
}

# =============================================================================
# TESTS: File Patterns
# =============================================================================

test_patterns_exist() {
    test_start "patterns exist"

    if [[ -n "$VDE_VM_NAME_PATTERN" ]] && \
       [[ -n "$VDE_SSH_PORT_PATTERN" ]]; then
        test_pass "patterns exist"
        return
    fi

    test_fail "patterns exist" "some patterns are missing"
}

test_vm_name_pattern() {
    test_start "VM name pattern"

    if echo "python123" | grep -qE "$VDE_VM_NAME_PATTERN"; then
        if ! echo "Python-VM" | grep -qE "$VDE_VM_NAME_PATTERN"; then
            test_pass "VM name pattern"
            return
        fi
    fi

    test_fail "VM name pattern" "pattern not working correctly"
}

# =============================================================================
# TESTS: Error Messages
# =============================================================================

test_error_messages_exist() {
    test_start "error messages exist"

    if [[ -n "$VDE_MSG_VM_NOT_FOUND" ]] && \
       [[ -n "$VDE_MSG_VM_EXISTS" ]] && \
       [[ -n "$VDE_MSG_INVALID_NAME" ]] && \
       [[ -n "$VDE_MSG_DOCKER_FAILED" ]] && \
       [[ -n "$VDE_MSG_TIMEOUT" ]] && \
       [[ -n "$VDE_MSG_LOCK_FAILED" ]] && \
       [[ -n "$VDE_MSG_NO_SSH_KEY" ]]; then
        test_pass "error messages exist"
        return
    fi

    test_fail "error messages exist" "some error messages are missing"
}

# =============================================================================
# Run All Tests
# =============================================================================

echo "=============================================="
echo "VDE Constants Unit Tests (Consistent Naming)"
echo "=============================================="

test_return_codes_exist
test_return_codes_values
test_port_ranges_exist
test_port_ranges_values
test_container_ssh_port
test_docker_config_exist
test_container_prefix
test_ssh_isolation_exist
test_ssh_paths_under_home
test_patterns_exist
test_vm_name_pattern
test_error_messages_exist

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
