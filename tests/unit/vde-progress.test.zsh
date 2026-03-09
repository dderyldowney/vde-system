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
source "$(dirname "$0")/../../lib/vde-progress"

# Test 1: format_time
test_start "_vde_progress_format_time formats durations"
output=$(_vde_progress_format_time 30)
if [[ "$output" == "30s" ]]; then
    test_pass "seconds formatted correctly"
else
    test_fail "seconds format incorrect" "expected '30s', got: $output"
fi

output=$(_vde_progress_format_time 65)
if [[ "$output" == "1m 5s" ]]; then
    test_pass "minutes formatted correctly"
else
    test_fail "minutes format incorrect" "expected '1m 5s', got: $output"
fi

# Test 2: progress_bar
test_start "vde_progress_bar operations"
output=$(vde_progress_bar_start "Test Bar" 100 2>&1)
if echo "$output" | grep -q "Test Bar"; then
    test_pass "progress bar start contains message"
else
    test_fail "progress bar start" "message not found in output"
fi

# Manually set state for update test since subshell lost it
_VDE_PROGRESS_BAR_TOTAL=100
_VDE_PROGRESS_BAR_MSG="Test Bar"
output=$(vde_progress_bar_update 50 2>&1)
if echo "$output" | grep -q "50%"; then
    test_pass "progress bar update shows percentage"
else
    test_fail "progress bar update" "50% not found in output"
fi

_VDE_PROGRESS_BAR_TOTAL=100
_VDE_PROGRESS_BAR_START=$(date +%s)
output=$(vde_progress_bar_stop "Done" 2>&1)
if echo "$output" | grep -q "Done"; then
    test_pass "progress bar stop shows message"
else
    test_fail "progress bar stop" "Done not found in output"
fi

# Test 3: spinner
test_start "vde_progress_spinner operations"
output=$(vde_progress_spinner_start "Spinning" 2>&1)
if echo "$output" | grep -q "Spinning"; then
    test_pass "spinner start contains message"
else
    test_fail "spinner start" "Spinning not found in output"
fi

_VDE_PROGRESS_SPINNER_MSG="Spinning"
output=$(vde_progress_spinner_update 2>&1)
if [[ -n "$output" ]]; then
    test_pass "spinner update produces output"
else
    test_fail "spinner update" "no output produced"
fi

_VDE_PROGRESS_SPINNER_START=$(date +%s)
output=$(vde_progress_spinner_stop "Finished" 2>&1)
if echo "$output" | grep -q "Finished"; then
    test_pass "spinner stop shows message"
else
    test_fail "spinner stop" "Finished not found in output"
fi

# Test 4: quiet_mode
test_start "vde_progress quiet mode"
vde_progress_set_quiet 1
output=$(vde_progress_info "Hidden" 2>&1)
if [[ -z "$output" ]]; then
    test_pass "quiet mode suppresses output"
else
    test_fail "quiet mode" "output was not suppressed: $output"
fi

vde_progress_set_quiet 0
output=$(vde_progress_info "Visible" 2>&1)
if echo "$output" | grep -q "Visible"; then
    test_pass "quiet mode disabled shows output"
else
    test_fail "quiet mode disabled" "Visible not found in output"
fi

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED