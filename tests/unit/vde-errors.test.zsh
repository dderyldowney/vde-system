#!/usr/bin/env zsh
# Test framework colors and counters
TESTS_PASSED=0
TESTS_FAILED=0
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

test_start() { echo -e "${YELLOW}Testing: $1${RESET}" }
test_pass() { echo -e "  ${GREEN}✓ PASS: $1${RESET}"; ((TESTS_PASSED++)) }
test_fail() { echo -e "  ${RED}✗ FAIL: $1 - $2${RESET}"; ((TESTS_FAILED++)) }

# Source dependencies and library under test
source "$(dirname "$0")/../../scripts/lib/vde-constants"
source "$(dirname "$0")/../../scripts/lib/vde-shell-compat"
source "$(dirname "$0")/../../scripts/lib/vde-errors"

# Test vde_error_simple
test_vde_error_simple() {
    test_start "vde_error_simple"
    local output=$(vde_error_simple "test error message" 2>&1)
    if echo "$output" | grep -q "test error message"; then
        test_pass "vde_error_simple"
        return
    fi
    test_fail "vde_error_simple" "error message not found in output"
}

# Test vde_error_show
test_vde_error_show() {
    test_start "vde_error_show"
    local output=$(vde_error_show "test issue" "test reason" "test solution" 2>&1)
    if echo "$output" | grep -q "test issue" && echo "$output" | grep -q "test reason"; then
        test_pass "vde_error_show"
        return
    fi
    test_fail "vde_error_show" "expected error components not found"
}

# Test vde_success
test_vde_success() {
    test_start "vde_success"
    local output=$(vde_success "test success message" 2>&1)
    if echo "$output" | grep -q "test success message"; then
        test_pass "vde_success"
        return
    fi
    test_fail "vde_success" "success message not found in output"
}

# Test vde_error_docker_not_running
test_vde_error_docker_not_running() {
    test_start "vde_error_docker_not_running"
    local output=$(vde_error_docker_not_running 2>&1)
    if echo "$output" | grep -qi "docker"; then
        test_pass "vde_error_docker_not_running"
        return
    fi
    test_fail "vde_error_docker_not_running" "docker error not shown"
}

# Test vde_error_vm_not_found
test_vde_error_vm_not_found() {
    test_start "vde_error_vm_not_found"
    local output=$(vde_error_vm_not_found "test-vm" 2>&1)
    if echo "$output" | grep -q "test-vm"; then
        test_pass "vde_error_vm_not_found"
        return
    fi
    test_fail "vde_error_vm_not_found" "VM name not in error message"
}

# Test vde_error_invalid_vm_name
test_vde_error_invalid_vm_name() {
    test_start "vde_error_invalid_vm_name"
    local output=$(vde_error_invalid_vm_name "bad@name!" 2>&1)
    if echo "$output" | grep -q "bad@name!"; then
        test_pass "vde_error_invalid_vm_name"
        return
    fi
    test_fail "vde_error_invalid_vm_name" "invalid name not in error message"
}

# Test vde_error_set_verbose and vde_error_is_verbose
test_vde_error_verbose() {
    test_start "vde_error_set_verbose and vde_error_is_verbose"
    vde_error_set_verbose 1
    if vde_error_is_verbose; then
        vde_error_set_verbose 0
        if ! vde_error_is_verbose; then
            test_pass "vde_error_verbose"
            return
        fi
    fi
    test_fail "vde_error_verbose" "verbose flag not working correctly"
}

# Test vde_error_with_code (should not exit in test)
test_vde_error_with_code() {
    test_start "vde_error_with_code"
    # Run in subshell to capture exit code
    (vde_error_with_code "test error" 42 2>&1) >/dev/null
    local exit_code=$?
    if [[ $exit_code -eq 42 ]]; then
        test_pass "vde_error_with_code"
        return
    fi
    test_fail "vde_error_with_code" "expected exit code 42, got $exit_code"
}

# Main runner
main() {
    echo ""
    echo "=========================================="
    echo "Unit Tests: vde-errors"
    echo "=========================================="

    test_vde_error_simple
    test_vde_error_show
    test_vde_success
    test_vde_error_docker_not_running
    test_vde_error_vm_not_found
    test_vde_error_invalid_vm_name
    test_vde_error_verbose
    test_vde_error_with_code

    echo ""
    echo -e "${GREEN}Passed:  $TESTS_PASSED${RESET}"
    echo -e "${RED}Failed:  $TESTS_FAILED${RESET}"
    [[ $TESTS_FAILED -eq 0 ]] && exit 0 || exit 1
}

main "$@"
