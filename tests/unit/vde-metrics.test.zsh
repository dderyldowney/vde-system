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
source "$(dirname "$0")/../../scripts/lib/vde-metrics"

# Set test environment
export VDE_METRICS_FILE="/tmp/vde-test-metrics-$$"
export VDE_LOG_FILE="/tmp/vde-test-log-$$"

# Test 1: metrics_init
test_start "vde_metrics_init creates metrics file"
vde_metrics_init
if [[ -f "$VDE_METRICS_FILE" ]]; then
    test_pass "metrics file created"
else
    test_fail "metrics file not created" "expected file at $VDE_METRICS_FILE"
fi

# Test 2: metrics_record
test_start "vde_metrics_record stores metric value"
vde_metrics_record "test.metric" 42
retrieved=$(vde_metrics_get_value "test.metric")
if [[ "$retrieved" == "42" ]]; then
    test_pass "metric recorded and retrieved correctly"
else
    test_fail "metric value mismatch" "expected 42, got $retrieved"
fi

# Test 3: metrics_increment
test_start "vde_metrics_increment increases counter"
vde_metrics_record "test.counter" 10
vde_metrics_increment "test.counter"
new_value=$(vde_metrics_get_value "test.counter")
if [[ "$new_value" == "11" ]]; then
    test_pass "counter incremented"
else
    test_fail "counter not incremented" "expected 11, got $new_value"
fi

# Test 4: metrics_decrement
test_start "vde_metrics_decrement decreases counter"
vde_metrics_record "test.decr" 20
vde_metrics_decrement "test.decr"
new_value=$(vde_metrics_get_value "test.decr")
if [[ "$new_value" == "19" ]]; then
    test_pass "counter decremented"
else
    test_fail "counter not decremented" "expected 19, got $new_value"
fi

# Test 5: metrics_reset
test_start "vde_metrics_reset clears all metrics"
vde_metrics_record "test.reset1" 100
vde_metrics_record "test.reset2" 200
vde_metrics_reset
if [[ ! -s "$VDE_METRICS_FILE" ]] || [[ $(wc -l < "$VDE_METRICS_FILE" 2>/dev/null || echo 0) -eq 0 ]]; then
    test_pass "metrics reset successfully"
else
    test_fail "metrics not reset" "file still contains data"
fi

# Test 6: metrics_cache_hit
test_start "vde_metrics_cache_hit records hit"
vde_metrics_init
vde_metrics_cache_hit
hit_count=$(vde_metrics_get_value "cache.hits")
if [[ -n "$hit_count" ]] && [[ "$hit_count" -gt 0 ]]; then
    test_pass "cache hit recorded"
else
    test_fail "cache hit not recorded" "expected count > 0, got $hit_count"
fi

# Test 7: metrics_cache_miss
test_start "vde_metrics_cache_miss records miss"
vde_metrics_cache_miss
miss_count=$(vde_metrics_get_value "cache.misses")
if [[ -n "$miss_count" ]] && [[ "$miss_count" -gt 0 ]]; then
    test_pass "cache miss recorded"
else
    test_fail "cache miss not recorded" "expected count > 0, got $miss_count"
fi

# Cleanup
rm -f "/tmp/vde-test-metrics-$$" "/tmp/vde-test-log-$$"

# Summary
echo
echo "========================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${RESET}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${RESET}"
echo "========================================"

exit $TESTS_FAILED
