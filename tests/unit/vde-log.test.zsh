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

# Setup temporary root for log files
TEST_TMP_DIR=$(mktemp -d)
export VDE_ROOT_DIR="$TEST_TMP_DIR"
mkdir -p "$VDE_ROOT_DIR/logs"

# Mock dependencies
vde_shell_date_iso8601() { echo "2026-02-10T12:00:00Z"; }

# Source required libraries
source "$(dirname "$0")/../../scripts/lib/vde-constants"
source "$(dirname "$0")/../../scripts/lib/vde-shell-compat"
source "$(dirname "$0")/../../scripts/lib/vde-log"

# Test 1: level control
test_start "vde_log level control"
vde_log_set_level "DEBUG"
if [[ "$(vde_log_get_level)" == "DEBUG" ]]; then
    test_pass "set level to DEBUG"
else
    test_fail "set level to DEBUG" "got: $(vde_log_get_level)"
fi

# Test 2: text format
test_start "vde_log text format"
vde_log_set_format "text"
vde_log_set_level "INFO"
output=$(vde_log "INFO" "Test message" "test-comp" 2>&1)
if echo "$output" | grep -q "\[INFO \]" && echo "$output" | grep -q "test-comp" && echo "$output" | grep -q "Test message"; then
    test_pass "text format contains level, component, and message"
else
    test_fail "text format" "missing components: $output"
fi

# Test 3: json format
test_start "vde_log json format"
vde_log_set_format "json"
output=$(vde_log "WARN" "JSON message" "json-comp" "key=val" 2>&1)
if echo "$output" | grep -q '"level":"WARN"' && \
   echo "$output" | grep -q '"component":"json-comp"' && \
   echo "$output" | grep -q '"message":"JSON message"' && \
   echo "$output" | grep -q '"context":"key=val"'; then
    test_pass "json format contains all fields"
else
    test_fail "json format" "missing fields: $output"
fi

# Test 4: filtering
test_start "vde_log filtering"
vde_log_set_level "ERROR"
vde_log_set_format "text"
output=$(vde_log "INFO" "Should be filtered" "test" 2>&1)
if [[ -z "$output" ]]; then
    test_pass "INFO message filtered when level is ERROR"
else
    test_fail "filtering" "INFO message was not filtered: $output"
fi

# Test 5: file output
test_start "vde_log file output"
LOG_FILE="$VDE_ROOT_DIR/logs/test.log"
vde_log_to_file "$LOG_FILE"
vde_log_set_level "INFO"
vde_log_info "Message to file" "file-test" >/dev/null 2>&1
if grep -q "Message to file" "$LOG_FILE"; then
    test_pass "log written to file"
else
    test_fail "file output" "log not found in file"
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