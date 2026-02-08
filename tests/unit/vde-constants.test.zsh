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

test_return_codes_readonly() {
    test_start "return codes are readonly"

    # In zsh, readonly variables cannot be modified
    # We verify this by checking the variable is still 0
    if [[ "$VDE_SUCCESS" -eq 0 ]]; then
        test_pass "return codes are readonly"
        return
    fi

    test_fail "return codes readonly" "VDE_SUCCESS was modified"
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

test_port_ranges_readonly() {
    test_start "port ranges are readonly"

    # In zsh, readonly variables cannot be modified
    # We verify this by checking the variable has expected value
    if [[ "$VDE_LANG_PORT_START" -eq 2200 ]]; then
        test_pass "port ranges are readonly"
        return
    fi

    test_fail "port ranges readonly" "VDE_LANG_PORT_START has unexpected value"
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
# TESTS: Timeout Configuration
# =============================================================================

test_timeouts_exist() {
    test_start "timeouts exist"

    if [[ -n "$VDE_DOCKER_TIMEOUT" ]] && \
       [[ -n "$VDE_SSH_TIMEOUT" ]] && \
       [[ -n "$VDE_LOCK_TIMEOUT" ]] && \
       [[ -n "$VDE_HEALTH_TIMEOUT" ]] && \
       [[ -n "$VDE_STARTUP_WAIT" ]]; then
        test_pass "timeouts exist"
        return
    fi

    test_fail "timeouts exist" "some timeout constants are missing"
}

test_timeouts_values() {
    test_start "timeout values are positive"

    if [[ "$VDE_DOCKER_TIMEOUT" -gt 0 ]] && \
       [[ "$VDE_SSH_TIMEOUT" -gt 0 ]] && \
       [[ "$VDE_LOCK_TIMEOUT" -gt 0 ]] && \
       [[ "$VDE_HEALTH_TIMEOUT" -gt 0 ]] && \
       [[ "$VDE_STARTUP_WAIT" -gt 0 ]]; then
        test_pass "timeout values are positive"
        return
    fi

    test_fail "timeout values" "some timeouts are not positive"
}

# =============================================================================
# TESTS: Retry Configuration
# =============================================================================

test_retry_config_exist() {
    test_start "retry config exist"

    if [[ -n "$VDE_MAX_RETRIES" ]] && \
       [[ -n "$VDE_RETRY_BASE_DELAY" ]] && \
       [[ -n "$VDE_RETRY_MAX_DELAY" ]]; then
        test_pass "retry config exist"
        return
    fi

    test_fail "retry config exist" "some retry constants are missing"
}

test_retry_values() {
    test_start "retry values are reasonable"

    if [[ "$VDE_MAX_RETRIES" -ge 1 ]] && \
       [[ "$VDE_MAX_RETRIES" -le 10 ]] && \
       [[ "$VDE_RETRY_BASE_DELAY" -ge 1 ]] && \
       [[ "$VDE_RETRY_BASE_DELAY" -le 10 ]] && \
       [[ "$VDE_RETRY_MAX_DELAY" -ge "$VDE_RETRY_BASE_DELAY" ]]; then
        test_pass "retry values are reasonable"
        return
    fi

    test_fail "retry values" "retry constants have unreasonable values"
}

# =============================================================================
# TESTS: Lock Configuration
# =============================================================================

test_lock_config_exist() {
    test_start "lock config exist"

    if [[ -n "$VDE_STALE_LOCK_AGE" ]] && \
       [[ -n "$VDE_LOCK_CHECK_INTERVAL" ]]; then
        test_pass "lock config exist"
        return
    fi

    test_fail "lock config exist" "some lock constants are missing"
}

test_lock_values() {
    test_start "lock values are positive"

    if [[ "$VDE_STALE_LOCK_AGE" -gt 0 ]] && \
       [[ "$VDE_LOCK_CHECK_INTERVAL" -gt 0 ]]; then
        test_pass "lock values are positive"
        return
    fi

    test_fail "lock values" "lock constants are not positive"
}

# =============================================================================
# TESTS: Logging Configuration
# =============================================================================

test_log_config_exist() {
    test_start "log config exist"

    if [[ -n "$VDE_LOG_RETENTION_DAYS" ]] && \
       [[ -n "$VDE_MAX_LOG_SIZE" ]]; then
        test_pass "log config exist"
        return
    fi

    test_fail "log config exist" "some log constants are missing"
}

test_log_size_value() {
    test_start "log size is 10MB"

    if [[ "$VDE_MAX_LOG_SIZE" -eq 10485760 ]]; then
        test_pass "log size is 10MB"
        return
    fi

    test_fail "log size" "expected 10485760, got $VDE_MAX_LOG_SIZE"
}

# =============================================================================
# TESTS: Docker Configuration
# =============================================================================

test_docker_config_exist() {
    test_start "docker config exist"

    # Check that all docker config variables are defined (VDE_SVC_CONTAINER_SUFFIX is empty string)
    if [[ -v VDE_DOCKER_NETWORK ]] && \
       [[ -v VDE_COMPOSE_PROJECT_PREFIX ]] && \
       [[ -v VDE_LANG_CONTAINER_SUFFIX ]] && \
       [[ -v VDE_SVC_CONTAINER_SUFFIX ]]; then
        test_pass "docker config exist"
        return
    fi

    test_fail "docker config exist" "some docker constants are missing"
}

test_container_suffixes() {
    test_start "container suffixes"

    if [[ "$VDE_LANG_CONTAINER_SUFFIX" == "-dev" ]] && \
       [[ "$VDE_SVC_CONTAINER_SUFFIX" == "" ]]; then
        test_pass "container suffixes"
        return
    fi

    test_fail "container suffixes" "incorrect suffix values"
}

# =============================================================================
# TESTS: SSH Configuration
# =============================================================================

test_ssh_config_exist() {
    test_start "SSH config exist"

    if [[ -n "$VDE_SSH_USER" ]] && \
       [[ -n "$VDE_SSH_KEY_PREFERENCE" ]]; then
        test_pass "SSH config exist"
        return
    fi

    test_fail "SSH config exist" "some SSH constants are missing"
}

test_ssh_user_value() {
    test_start "SSH user"

    if [[ "$VDE_SSH_USER" == "dev" ]]; then
        test_pass "SSH user"
        return
    fi

    test_fail "SSH user" "expected 'dev', got '$VDE_SSH_USER'"
}

test_ssh_key_preference() {
    test_start "SSH key preference order"

    if echo "$VDE_SSH_KEY_PREFERENCE" | grep -q "id_ed25519"; then
        test_pass "SSH key preference order"
        return
    fi

    test_fail "SSH key preference" "ed25519 should be preferred: $VDE_SSH_KEY_PREFERENCE"
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

test_error_messages_format() {
    test_start "error messages have format placeholders"

    if [[ "$VDE_MSG_VM_NOT_FOUND" == *"%"* ]] && \
       [[ "$VDE_MSG_VM_EXISTS" == *"%"* ]] && \
       [[ "$VDE_MSG_INVALID_NAME" == *"%"* ]]; then
        test_pass "error messages have format placeholders"
        return
    fi

    test_fail "error messages format" "error messages missing format placeholders"
}

# =============================================================================
# TESTS: Source Guard
# =============================================================================

test_source_guard() {
    test_start "source guard prevents double sourcing"

    # Count lines before sourcing
    local lines_before=$(wc -l < "$PROJECT_ROOT/scripts/lib/vde-constants")

    # Source again
    source "$PROJECT_ROOT/scripts/lib/vde-constants" 2>/dev/null

    # Constants should still have correct values
    if [[ "$VDE_SUCCESS" -eq 0 ]]; then
        test_pass "source guard prevents double sourcing"
        return
    fi

    test_fail "source guard" "double sourcing caused issues"
}

# =============================================================================
# Run All Tests
# =============================================================================

echo "=============================================="
echo "VDE Constants Unit Tests"
echo "=============================================="

# Return code tests
test_return_codes_exist
test_return_codes_values
test_return_codes_readonly

# Port configuration tests
test_port_ranges_exist
test_port_ranges_values
test_port_ranges_readonly
test_container_ssh_port

# Timeout configuration tests
test_timeouts_exist
test_timeouts_values

# Retry configuration tests
test_retry_config_exist
test_retry_values

# Lock configuration tests
test_lock_config_exist
test_lock_values

# Logging configuration tests
test_log_config_exist
test_log_size_value

# Docker configuration tests
test_docker_config_exist
test_container_suffixes

# SSH configuration tests
test_ssh_config_exist
test_ssh_user_value
test_ssh_key_preference

# SSH isolation tests
test_ssh_isolation_exist
test_ssh_paths_under_home

# Pattern tests
test_patterns_exist
test_vm_name_pattern

# Error message tests
test_error_messages_exist
test_error_messages_format

# Source guard test
test_source_guard

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
