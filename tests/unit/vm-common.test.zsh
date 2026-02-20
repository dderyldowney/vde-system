#!/usr/bin/env zsh
# Unit Tests for vm-common Library
# Tests core VM management functions

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source the library under test
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vde-naming"
source "$PROJECT_ROOT/scripts/lib/vm-common"

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

# Test helpers
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
# TESTS: VM Type Loading
# =============================================================================

test_load_vm_types() {
    test_start "load_vm_types"

    # Force reload
    load_vm_types --no-cache

    # Check that VM types are loaded using canonical prefixed name
    local python_type
    python_type=$(get_vm_info type "vde-python")
    if [[ "$python_type" == "lang" ]]; then
        test_pass "load_vm_types"
        return
    fi

    test_fail "load_vm_types" "vde-python type not loaded correctly"
}

test_resolve_vm_name() {
    test_start "resolve_vm_name (to canonical prefixed name)"

    # Resolve from alias
    local result
    result=$(resolve_vm_name "python3")
    if [[ "$result" == "vde-python" ]]; then
        test_pass "resolve_vm_name (alias -> prefixed)"
    else
        test_fail "resolve_vm_name alias" "expected 'vde-python', got '$result'"
        return
    fi

    # Resolve from raw name
    result=$(resolve_vm_name "python")
    if [[ "$result" == "vde-python" ]]; then
        test_pass "resolve_vm_name (raw -> prefixed)"
    else
        test_fail "resolve_vm_name raw" "expected 'vde-python', got '$result'"
    fi
}

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "Unit Tests: vm-common (Canonical Prefixed Naming)"
    echo "=========================================="
    echo ""

    test_load_vm_types
    test_resolve_vm_name

    # Print summary
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo -e "${GREEN}Passed:  $TESTS_PASSED${RESET}"
    echo -e "${RED}Failed:  $TESTS_FAILED${RESET}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}All tests passed!${RESET}\n"
        exit 0
    else
        echo -e "\n${RED}Some tests failed!${RESET}\n"
        exit 1
    fi
}

main "$@"
