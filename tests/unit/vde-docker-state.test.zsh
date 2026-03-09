#!/usr/bin/env zsh
# Unit Tests for vde-docker-state Library
# Tests Docker container state query functions

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/lib/vde-shell-compat"
source "$PROJECT_ROOT/lib/vde-constants"
source "$PROJECT_ROOT/lib/vde-naming"
source "$PROJECT_ROOT/lib/vm-common"
source "$PROJECT_ROOT/lib/vde-docker-state"

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
# TESTS: _get_container_name (Should include vde- prefix)
# =============================================================================

test_get_container_name_raw() {
    test_start "get container name (raw)"

    local result
    result=$(_get_container_name "python")
    if [[ "$result" == "vde-python" ]]; then
        test_pass "get container name (raw)"
        return
    fi

    test_fail "get container name raw" "expected 'vde-python', got '$result'"
}

test_get_container_name_idempotent() {
    test_start "get container name (idempotent)"

    local result
    result=$(_get_container_name "vde-python")
    if [[ "$result" == "vde-python" ]]; then
        test_pass "get container name (idempotent)"
        return
    fi

    test_fail "get container name idempotent" "expected 'vde-python', got '$result'"
}

# =============================================================================
# Run All Tests
# =============================================================================

echo "=============================================="
echo "VDE Docker State Unit Tests (Prefixed Naming)"
echo "=============================================="

test_get_container_name_raw
test_get_container_name_idempotent

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
