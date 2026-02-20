#!/usr/bin/env zsh
# Unit Tests for vde-naming Library
# Tests VM naming conventions and validation functions

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vde-naming"

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
# TESTS: Pattern Definitions
# =============================================================================

test_patterns_exist() {
    test_start "naming patterns exist"

    if [[ -n "$VDE_NAME_PATTERN" ]]; then
        test_pass "naming patterns exist"
        return
    fi

    test_fail "naming patterns exist" "patterns are missing"
}

# =============================================================================
# TESTS: vde_validate_name
# =============================================================================

test_validate_name_empty() {
    test_start "validate name (empty)"

    if ! vde_validate_name "" >/dev/null 2>&1; then
        test_pass "validate name (empty)"
        return
    fi

    test_fail "validate name empty" "empty name should be rejected"
}

test_validate_name_valid() {
    test_start "validate name (valid with prefix)"

    if vde_validate_name "vde-python" >/dev/null 2>&1; then
        test_pass "validate name (valid with prefix)"
        return
    fi

    test_fail "validate name valid" "valid name vde-python was rejected"
}

test_validate_name_raw() {
    test_start "validate name (raw name allowed)"

    if vde_validate_name "python" >/dev/null 2>&1; then
        test_pass "validate name (raw name allowed)"
        return
    fi

    test_fail "validate name raw" "raw name python was rejected"
}

# =============================================================================
# TESTS: vde_normalize_name (Should return raw canonical name)
# =============================================================================

test_normalize_name_lowercase() {
    test_start "normalize name (lowercase)"

    local result
    result=$(vde_normalize_name "PYTHON")
    if [[ "$result" == "python" ]]; then
        test_pass "normalize name (lowercase)"
        return
    fi

    test_fail "normalize name lowercase" "expected 'python', got '$result'"
}

test_normalize_name_strip_prefix() {
    test_start "normalize name (strip vde- prefix)"

    local result
    result=$(vde_normalize_name "vde-python")
    if [[ "$result" == "python" ]]; then
        test_pass "normalize name (strip vde- prefix)"
        return
    fi

    test_fail "normalize name prefix" "expected 'python', got '$result'"
}

# =============================================================================
# TESTS: vde_get_container_name (Should add prefix)
# =============================================================================

test_get_container_name() {
    test_start "get container name"

    local result
    result=$(vde_get_container_name "python")
    if [[ "$result" == "vde-python" ]]; then
        test_pass "get container name"
        return
    fi

    test_fail "get container name" "expected 'vde-python', got '$result'"
}

test_get_container_name_idempotent() {
    test_start "get container name (idempotent)"

    local result
    result=$(vde_get_container_name "vde-python")
    if [[ "$result" == "vde-python" ]]; then
        test_pass "get container name (idempotent)"
        return
    fi

    test_fail "get container name idempotent" "expected 'vde-python', got '$result'"
}

# =============================================================================
# TESTS: vde_get_ssh_host
# =============================================================================

test_get_ssh_host() {
    test_start "get ssh host"

    local result
    result=$(vde_get_ssh_host "python")
    if [[ "$result" == "vde-python" ]]; then
        test_pass "get ssh host"
        return
    fi

    test_fail "get ssh host" "expected 'vde-python', got '$result'"
}

# =============================================================================
# Run All Tests
# =============================================================================

echo "=============================================="
echo "VDE Naming Unit Tests (Raw Canonical Naming)"
echo "=============================================="

test_patterns_exist
test_validate_name_empty
test_validate_name_valid
test_validate_name_raw
test_normalize_name_lowercase
test_normalize_name_strip_prefix
test_get_container_name
test_get_container_name_idempotent
test_get_ssh_host

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
