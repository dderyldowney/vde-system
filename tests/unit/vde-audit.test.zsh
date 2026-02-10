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

# Setup temporary root for audit files
TEST_TMP_DIR=$(mktemp -d)
export VDE_ROOT_DIR="$TEST_TMP_DIR"
mkdir -p "$VDE_ROOT_DIR/logs"

# Mock dependencies
vde_shell_date_iso8601() { echo "2026-02-10T12:00:00Z"; }
vde_log_info() { :; }
vde_log_init() { :; }
_VDE_LOG_INITIALIZED=1
whoami() { echo "testuser"; }
hostname() { echo "testhost"; }

# Source required libraries
source "$(dirname "$0")/../../scripts/lib/vde-constants"
source "$(dirname "$0")/../../scripts/lib/vde-shell-compat"
source "$(dirname "$0")/../../scripts/lib/vde-log"
source "$(dirname "$0")/../../scripts/lib/vde-audit"

# Test 1: initialization
test_start "vde_audit initialization"
if vde_audit_init; then
    test_pass "initialization success"
else
    test_fail "initialization" "vde_audit_init failed"
fi

if [[ -f "$VDE_AUDIT_LOG" ]]; then
    test_pass "audit log file created"
else
    test_fail "audit log file" "file not found: $VDE_AUDIT_LOG"
fi

# Test 2: audit logging
test_start "vde_audit logging"
vde_audit_log "create_vm" "success" "vm_name=test-python"
last_line=$(tail -n 1 "$VDE_AUDIT_LOG")
if echo "$last_line" | grep -q "create_vm" && echo "$last_line" | grep -q "success" && echo "$last_line" | grep -q "test-python"; then
    test_pass "audit entry format correct"
else
    test_fail "audit logging" "unexpected entry: $last_line"
fi

# Test 3: querying
test_start "vde_audit querying"
vde_audit_log "start_vm" "success" "vm_name=test-go"
output=$(vde_audit_by_user "testuser" 2>&1)
if echo "$output" | grep -q "test-go"; then
    test_pass "query by user works"
else
    test_fail "query by user" "entry not found in query results"
fi

output=$(vde_audit_by_operation "start_vm" 2>&1)
if echo "$output" | grep -q "start_vm"; then
    test_pass "query by operation works"
else
    test_fail "query by operation" "entry not found in query results"
fi

# Cleanup
rm -rf "$TEST_TMP_DIR"

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED