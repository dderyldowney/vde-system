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
source "$(dirname "$0")/../../scripts/lib/vde-progress"

# Test 1: format_time_seconds
test_start "_vde_progress_format_time formats seconds"
output=$(_vde_progress_format_time 45)
if echo "$output" | grep -q "45s"; then
    test_pass "seconds formatted correctly"
else
    test_fail "seconds format incorrect" "expected '45s' in output, got: $output"
fi

# Test 2: format_time_minutes
test_start "_vde_progress_format_time formats minutes"
output=$(_vde_progress_format_time 150)
if echo "$output" | grep -q "2m"; then
    test_pass "minutes formatted correctly"
else
    test_fail "minutes format incorrect" "expected '2m' in output, got: $output"
fi

# Test 3: progress_info
test_start "vde_progress_info displays message"
output=$(vde_progress_info "test msg" 2>&1)
if echo "$output" | grep -q "test msg"; then
    test_pass "info message displayed"
else
    test_fail "info message not displayed" "expected 'test msg' in output"
fi

# Test 4: progress_warn
test_start "vde_progress_warn displays warning"
output=$(vde_progress_warn "warning" 2>&1)
if echo "$output" | grep -q "warning"; then
    test_pass "warning message displayed"
else
    test_fail "warning message not displayed" "expected 'warning' in output"
fi

# Test 5: progress_error
test_start "vde_progress_error displays error"
output=$(vde_progress_error "err msg" 2>&1)
if echo "$output" | grep -q "err msg"; then
    test_pass "error message displayed"
else
    test_fail "error message not displayed" "expected 'err msg' in output"
fi

# Test 6: progress_done
test_start "vde_progress_done displays completion"
output=$(vde_progress_done "complete" 2>&1)
if echo "$output" | grep -q "complete"; then
    test_pass "completion message displayed"
else
    test_fail "completion message not displayed" "expected 'complete' in output"
fi

# Test 7: quiet_mode
test_start "is_quiet mode detection"
export QUIET_MODE=1
is_quiet
quiet_enabled=$?
unset QUIET_MODE
is_quiet
quiet_disabled=$?
if [[ $quiet_enabled -eq 0 ]] && [[ $quiet_disabled -ne 0 ]]; then
    test_pass "quiet mode detection works"
else
    test_fail "quiet mode detection failed" "expected 0 when set, non-zero when unset"
fi

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED
