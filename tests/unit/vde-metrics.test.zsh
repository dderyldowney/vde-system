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

# Setup temporary root for metrics files
TEST_TMP_DIR=$(mktemp -d)
export VDE_ROOT_DIR="$TEST_TMP_DIR"
mkdir -p "$VDE_ROOT_DIR/.cache"

# Mock dependencies
vde_shell_date_iso8601() { echo "2026-02-10T12:00:00Z"; }
vde_shell_date_epoch() { date +%s; }
vde_log_info() { :; }
vde_log_debug() { :; }
vde_log_warn() { :; }
vde_log_error() { :; }

# Source required libraries
source "$(dirname "$0")/../../lib/vde-constants"
source "$(dirname "$0")/../../lib/vde-shell-compat"
source "$(dirname "$0")/../../lib/vde-log"
source "$(dirname "$0")/../../lib/vde-metrics"

# Test 1: initialization
test_start "vde_metrics initialization"
if vde_metrics_init; then
    test_pass "initialization success"
else
    test_fail "initialization" "vde_metrics_init failed"
fi

if [[ -f "$VDE_METRICS_FILE" ]]; then
    test_pass "metrics file created"
else
    test_fail "metrics file" "file not found: $VDE_METRICS_FILE"
fi

# Test 2: recording
test_start "vde_metrics recording"
vde_metrics_record "test.metric" 100 "ms"
val=$(vde_metrics_get_value "test.metric")
if [[ "$val" == "100" ]]; then
    test_pass "record and retrieve value correct"
else
    test_fail "recording" "expected 100, got: $val"
fi

# Test 3: timing
test_start "vde_metrics timing"
vde_metrics_timing_start "test_op"
sleep 0.1
vde_metrics_timing_end "test_op" "test.latency"
val=$(vde_metrics_get_value "test.latency")
if [[ "$val" -ge 0 ]]; then
    test_pass "timing recorded value"
else
    test_fail "timing" "no value recorded for latency"
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