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

# Setup temp log file
export VDE_LOG_FILE="/tmp/vde-test-log-$$"
export VDE_LOG_DIR="$(dirname "$VDE_LOG_FILE")"

# Source dependencies and library under test
source "$(dirname "$0")/../../scripts/lib/vde-constants"
source "$(dirname "$0")/../../scripts/lib/vde-shell-compat"
source "$(dirname "$0")/../../scripts/lib/vde-log"

# Test vde_log_init
test_vde_log_init() {
    test_start "vde_log_init"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    if [[ -f "$VDE_LOG_FILE" ]]; then
        test_pass "vde_log_init creates log file"
        return
    fi
    test_fail "vde_log_init" "log file not created"
}

# Test vde_log_set_level and vde_log_get_level
test_vde_log_level() {
    test_start "vde_log_set_level and vde_log_get_level"
    vde_log_set_level "WARN"
    local level=$(vde_log_get_level)
    if [[ "$level" == "WARN" ]]; then
        test_pass "vde_log_set_level and vde_log_get_level"
        return
    fi
    test_fail "vde_log_level" "expected 'WARN', got '$level'"
}

# Test vde_log_set_format
test_vde_log_format() {
    test_start "vde_log_set_format"
    vde_log_set_format "json"
    if [[ "${VDE_LOG_FORMAT:-text}" == "json" ]]; then
        test_pass "vde_log_set_format"
        return
    fi
    test_fail "vde_log_format" "format not set to json"
}

# Test vde_log writes to file
test_vde_log_write() {
    test_start "vde_log writes to file"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    vde_log_set_level "DEBUG"
    vde_log "INFO" "test message" "test-component"
    if [[ -s "$VDE_LOG_FILE" ]] && grep -q "test message" "$VDE_LOG_FILE"; then
        test_pass "vde_log writes to file"
        return
    fi
    test_fail "vde_log_write" "message not found in log file"
}

# Test vde_log_debug
test_vde_log_debug() {
    test_start "vde_log_debug"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    vde_log_set_level "DEBUG"
    vde_log_debug "debug test message"
    if grep -q "debug test message" "$VDE_LOG_FILE" && grep -q "DEBUG" "$VDE_LOG_FILE"; then
        test_pass "vde_log_debug"
        return
    fi
    test_fail "vde_log_debug" "debug message not logged"
}

# Test vde_log_info
test_vde_log_info() {
    test_start "vde_log_info"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    vde_log_set_level "INFO"
    vde_log_info "info test message"
    if grep -q "info test message" "$VDE_LOG_FILE" && grep -q "INFO" "$VDE_LOG_FILE"; then
        test_pass "vde_log_info"
        return
    fi
    test_fail "vde_log_info" "info message not logged"
}

# Test vde_log_warn
test_vde_log_warn() {
    test_start "vde_log_warn"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    vde_log_set_level "WARN"
    vde_log_warn "warn test message"
    if grep -q "warn test message" "$VDE_LOG_FILE" && grep -q "WARN" "$VDE_LOG_FILE"; then
        test_pass "vde_log_warn"
        return
    fi
    test_fail "vde_log_warn" "warn message not logged"
}

# Test vde_log_error
test_vde_log_error() {
    test_start "vde_log_error"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    vde_log_set_level "ERROR"
    vde_log_error "error test message"
    if grep -q "error test message" "$VDE_LOG_FILE" && grep -q "ERROR" "$VDE_LOG_FILE"; then
        test_pass "vde_log_error"
        return
    fi
    test_fail "vde_log_error" "error message not logged"
}

# Test vde_log_recent
test_vde_log_recent() {
    test_start "vde_log_recent"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    vde_log_set_level "INFO"
    vde_log_info "message 1"
    vde_log_info "message 2"
    vde_log_info "message 3"
    local recent=$(vde_log_recent 2)
    if [[ $(echo "$recent" | wc -l) -eq 2 ]]; then
        test_pass "vde_log_recent"
        return
    fi
    test_fail "vde_log_recent" "expected 2 lines, got $(echo "$recent" | wc -l)"
}

# Test vde_log_grep
test_vde_log_grep() {
    test_start "vde_log_grep"
    rm -f "$VDE_LOG_FILE"
    vde_log_init
    vde_log_set_level "INFO"
    vde_log_info "findme unique pattern"
    vde_log_info "another message"
    local result=$(vde_log_grep "findme")
    if echo "$result" | grep -q "findme unique pattern"; then
        test_pass "vde_log_grep"
        return
    fi
    test_fail "vde_log_grep" "pattern not found"
}

# Cleanup
cleanup() {
    rm -f "$VDE_LOG_FILE"
}

# Main runner
main() {
    echo ""
    echo "=========================================="
    echo "Unit Tests: vde-log"
    echo "=========================================="

    test_vde_log_init
    test_vde_log_level
    test_vde_log_format
    test_vde_log_write
    test_vde_log_debug
    test_vde_log_info
    test_vde_log_warn
    test_vde_log_error
    test_vde_log_recent
    test_vde_log_grep

    cleanup

    echo ""
    echo -e "${GREEN}Passed:  $TESTS_PASSED${RESET}"
    echo -e "${RED}Failed:  $TESTS_FAILED${RESET}"
    [[ $TESTS_FAILED -eq 0 ]] && exit 0 || exit 1
}

main "$@"
