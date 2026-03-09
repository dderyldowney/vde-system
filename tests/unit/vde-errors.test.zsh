#!/usr/bin/env zsh
# Test framework
TESTS_PASSED=0
TESTS_FAILED=0
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'
test_start() { echo -e "${YELLOW}Testing: $1${RESET}" }
test_pass() { echo -e "  ${GREEN}✓ PASS: $1${RESET}"; ((TESTS_PASSED++)) }
test_fail() { echo -e "  ${RED}✗ FAIL: $1 - $2${RESET}"; ((TESTS_FAILED++)) }

# Source required libraries
source "$(dirname "$0")/../../lib/vde-constants"
source "$(dirname "$0")/../../lib/vde-shell-compat"
source "$(dirname "$0")/../../lib/vde-errors"

# Force no colors for easier testing
VDE_ERRORS_COLOR_RESET=''
VDE_ERRORS_COLOR_ERROR=''
VDE_ERRORS_COLOR_WARNING=''
VDE_ERRORS_COLOR_INFO=''
VDE_ERRORS_COLOR_SUCCESS=''
VDE_ERRORS_COLOR_DIM=''
VDE_ERRORS_COLOR_LINK=''

# Test 1: vde_error_simple
test_start "vde_error_simple"
output=$(vde_error_simple "Test simple error" 2>&1)
if echo "$output" | grep -q "Error: Test simple error"; then
    test_pass "simple error output correct"
else
    test_fail "simple error output" "expected 'Error: Test simple error', got: $output"
fi

# Test 2: vde_error_show
test_start "vde_error_show"
output=$(vde_error_show "Something failed" "Reason X" "Do Y" 2>&1)
if echo "$output" | grep -q "Error: Something failed" && \
   echo "$output" | grep -q "Reason: Reason X" && \
   echo "$output" | grep -q "Solution:" && \
   echo "$output" | grep -q "Do Y"; then
    test_pass "full error output contains all components"
else
    test_fail "full error output" "missing components in output: $output"
fi

# Test 3: common errors
test_start "common error functions"
output=$(vde_error_docker_not_running 2>&1)
if echo "$output" | grep -q "Cannot connect to Docker daemon"; then
    test_pass "docker_not_running error correct"
else
    test_fail "docker_not_running error" "unexpected output: $output"
fi

output=$(vde_error_vm_not_found "test-vm" 2>&1)
if echo "$output" | grep -q "VM 'test-vm' not found"; then
    test_pass "vm_not_found error correct"
else
    test_fail "vm_not_found error" "unexpected output: $output"
fi

# Test 4: success
test_start "vde_success"
output=$(vde_success "Operation complete" 2>&1)
if echo "$output" | grep -q "Operation complete"; then
    test_pass "success message correct"
else
    test_fail "success message" "unexpected output: $output"
fi

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED