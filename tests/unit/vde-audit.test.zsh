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
source "$(dirname "$0")/../../scripts/lib/vde-log"
source "$(dirname "$0")/../../scripts/lib/vde-audit"

# Set test environment
export VDE_AUDIT_LOG="/tmp/vde-test-audit-$$"
export VDE_LOG_FILE="/tmp/vde-test-log-$$"

# Test 1: audit_init
test_start "vde_audit_init creates audit log file"
vde_audit_init
if [[ -f "$VDE_AUDIT_LOG" ]]; then
    test_pass "audit log file created"
else
    test_fail "audit log file not created" "expected file at $VDE_AUDIT_LOG"
fi

# Test 2: audit_log
test_start "vde_audit_log writes entry with correct format"
vde_audit_log "test_operation" "test_vm" "SUCCESS" "test details"
if grep -q "|" "$VDE_AUDIT_LOG" && grep -q "test_operation" "$VDE_AUDIT_LOG"; then
    test_pass "audit entry logged with pipe-delimited format"
else
    test_fail "audit entry format incorrect" "expected pipe-delimited entry"
fi

# Test 3: audit_create_vm
test_start "vde_audit_create_vm logs VM creation"
vde_audit_create_vm "test-vm-001" "SUCCESS"
if grep -q "create" "$VDE_AUDIT_LOG" && grep -q "test-vm-001" "$VDE_AUDIT_LOG"; then
    test_pass "VM creation audited"
else
    test_fail "VM creation not audited" "expected 'create' and 'test-vm-001' in log"
fi

# Test 4: audit_query
test_start "vde_audit_query finds matching entries"
vde_audit_log "query_test_op" "query_vm" "SUCCESS" "query details"
result=$(vde_audit_query "query_test_op")
if [[ -n "$result" ]] && echo "$result" | grep -q "query_test_op"; then
    test_pass "audit query found matches"
else
    test_fail "audit query failed" "expected to find 'query_test_op'"
fi

# Test 5: audit_recent
test_start "vde_audit_recent returns correct count"
vde_audit_log "recent1" "vm1" "SUCCESS" "details1"
vde_audit_log "recent2" "vm2" "SUCCESS" "details2"
vde_audit_log "recent3" "vm3" "SUCCESS" "details3"
recent=$(vde_audit_recent 2)
line_count=$(echo "$recent" | wc -l | tr -d ' ')
if [[ "$line_count" -eq 2 ]]; then
    test_pass "recent entries count correct"
else
    test_fail "recent entries count incorrect" "expected 2, got $line_count"
fi

# Test 6: audit_failures
test_start "vde_audit_failures finds failure entries"
vde_audit_log "failure_test" "failure_vm" "FAILURE" "test failure"
failures=$(vde_audit_failures)
if [[ -n "$failures" ]] && echo "$failures" | grep -q "FAILURE"; then
    test_pass "failure entries found"
else
    test_fail "failure entries not found" "expected FAILURE in output"
fi

# Test 7: audit_stats
test_start "vde_audit_stats returns statistics"
vde_audit_log "stats_op1" "vm1" "SUCCESS" "details"
vde_audit_log "stats_op2" "vm2" "SUCCESS" "details"
stats=$(vde_audit_stats)
if [[ -n "$stats" ]]; then
    test_pass "audit stats generated"
else
    test_fail "audit stats empty" "expected non-empty statistics"
fi

# Cleanup
rm -f "/tmp/vde-test-audit-$$" "/tmp/vde-test-log-$$"

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED
