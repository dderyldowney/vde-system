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
source "$(dirname "$0")/../../scripts/lib/vde-constants"
source "$(dirname "$0")/../../scripts/lib/vde-shell-compat"
source "$(dirname "$0")/../../scripts/lib/vm-common"
source "$(dirname "$0")/../../scripts/lib/vde-health"

# Set test environment
export VDE_LOG_FILE="/tmp/vde-test-log-$$"

# Test 1: check_container_nonexistent
test_start "vde_check_container_running fails on non-existent container"
vde_check_container_running "nonexistent-container-xyz-$$" 2>/dev/null
if [[ $? -ne 0 ]]; then
    test_pass "non-existent container check returned failure"
else
    test_fail "non-existent container check" "expected non-zero return code"
fi

# Test 2: health_check_nonexistent
test_start "vde_health_check fails on non-existent VM"
vde_health_check "nonexistent-vm-xyz-$$" 2>/dev/null
if [[ $? -ne 0 ]]; then
    test_pass "health check on non-existent VM returned failure"
else
    test_fail "health check on non-existent VM" "expected non-zero return code"
fi

# Test 3: check_ssh_port_unavailable
test_start "vde_check_ssh_port fails on unavailable host"
vde_check_ssh_port "192.0.2.255" 22 1 2>/dev/null
if [[ $? -ne 0 ]]; then
    test_pass "SSH port check on unavailable host returned failure"
else
    test_fail "SSH port check on unavailable host" "expected timeout/failure"
fi

# Test 4: health_functions_exist
test_start "vde_health_check function exists"
if type -f vde_health_check &>/dev/null; then
    test_pass "vde_health_check function defined"
else
    test_fail "vde_health_check function not found" "expected function to exist"
fi

# Test 5: check_container_running_function
test_start "vde_check_container_running function exists"
if type -f vde_check_container_running &>/dev/null; then
    test_pass "vde_check_container_running function defined"
else
    test_fail "vde_check_container_running function not found" "expected function to exist"
fi

# Cleanup
rm -f "/tmp/vde-test-log-$$"

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED
