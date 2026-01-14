#!/usr/bin/env zsh
# VDE Test Suite Runner
# Runs all tests and produces a comprehensive report

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Test configuration
VERBOSE=${VERBOSE:-false}
PARALLEL=${PARALLEL:-false}
TEST_SELECTOR="${TEST_SELECTOR:-all}"

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    CYAN=''
    BOLD=''
    RESET=''
fi

# Test results
declare -A TEST_RESULTS
TOTAL_TESTS=0
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_SKIPPED=0
TOTAL_RUN=0

# Test suites
declare -a TEST_SUITES
declare -a TEST_SUITE_NAMES
declare -a TEST_SUITE_PATHS

# =============================================================================
# USAGE
# =============================================================================

show_usage() {
    cat <<EOF
${BOLD}VDE Test Suite Runner${RESET}

Usage: $0 [OPTIONS] [TEST_SELECTOR]

${BOLD}TEST SELECTORS:${RESET}
  all                    Run all tests (default)
  bug-fix                Run bug fix validation tests only
  unit                   Run unit tests only
  integration            Run integration tests only
  <specific_test>        Run a specific test file

${BOLD}OPTIONS:${RESET}
  -v, --verbose          Show detailed test output
  -p, --parallel         Run tests in parallel (experimental)
  -h, --help             Show this help message
  --list                 List all available test suites

${BOLD}EXAMPLES:${RESET}
  $0                      # Run all tests
  $0 unit                 # Run only unit tests
  $0 -v bug-fix           # Run bug fix tests with verbose output
  $0 unit/vm-common       # Run specific unit test

${BOLD}TEST STRUCTURE:${RESET}
  tests/
  ├── bug-fix-validation.test.sh   # Bug fix validation tests
  ├── unit/                         # Unit tests for each library
  │   ├── vm-common.test.sh
  │   ├── vde-shell-compat.test.sh
  │   ├── vde-parser.test.sh
  │   └── ...
  ├── integration/                  # Integration tests
  │   └── vm-lifecycle-integration.test.sh
  └── features/                     # BDD feature specifications
      ├── vm-lifecycle.feature
      ├── port-management.feature
      └── ...

EOF
}

# =============================================================================
# TEST DISCOVERY
# =============================================================================

discover_tests() {
    local selector="$1"

    case "$selector" in
        all)
            TEST_SUITES=(
                "Bug Fix Validation:bug-fix-validation"
                "Unit:vm-common"
                "Unit:vde-shell-compat"
                "Unit:vde-parser"
                "Integration:vm-lifecycle"
            )
            ;;
        bug-fix)
            TEST_SUITES=("Bug Fix Validation:bug-fix-validation")
            ;;
        unit)
            TEST_SUITES=(
                "Unit:vm-common"
                "Unit:vde-shell-compat"
                "Unit:vde-parser"
            )
            ;;
        integration)
            TEST_SUITES=("Integration:vm-lifecycle")
            ;;
        *)
            # Check if it's a specific test file
            if [[ -f "$SCRIPT_DIR/$selector.test.sh" ]]; then
                TEST_SUITES=("Custom:$selector")
            elif [[ -f "$SCRIPT_DIR/$selector" ]]; then
                TEST_SUITES=("Custom:$selector")
            else
                echo -e "${RED}Error: Test selector '$selector' not found${RESET}"
                echo ""
                show_usage
                exit 1
            fi
            ;;
    esac
}

list_tests() {
    echo -e "${BOLD}Available Test Suites:${RESET}"
    echo ""

    # Bug fix validation
    if [[ -f "$SCRIPT_DIR/bug-fix-validation.test.sh" ]]; then
        echo "  ${CYAN}bug-fix${RESET}         Bug fix validation tests"
    fi

    # Unit tests
    echo ""
    echo "  ${CYAN}unit${RESET}             Unit tests:"
    for test in "$SCRIPT_DIR"/unit/*.test.sh(N); do
        if [[ -f "$test" ]]; then
            local name="${test:t:r}"
            echo "    ${name}"
        fi
    done

    # Integration tests
    echo ""
    echo "  ${CYAN}integration${RESET}      Integration tests:"
    for test in "$SCRIPT_DIR"/integration/*.test.sh(N); do
        if [[ -f "$test" ]]; then
            local name="${test:t:r}"
            echo "    ${name}"
        fi
    done

    echo ""
}

# =============================================================================
# TEST EXECUTION
# =============================================================================

run_test_suite() {
    local suite_name="$1"
    local suite_id="$2"
    local test_file="$3"

    echo ""
    echo -e "${BLUE}========================================${RESET}"
    echo -e "${BLUE}Running:${RESET} ${BOLD}$suite_name${RESET}"
    echo -e "${BLUE}========================================${RESET}"
    echo ""

    local test_path="$SCRIPT_DIR/$test_file"
    if [[ ! -f "$test_path" ]]; then
        test_path="$test_file"
    fi

    if [[ ! -f "$test_path" ]]; then
        echo -e "${RED}Error: Test file not found: $test_path${RESET}"
        return 1
    fi

    # Run the test and capture output
    local output
    local exit_code

    if [[ "$VERBOSE" == "true" ]]; then
        output=$(zsh "$test_path" 2>&1)
        exit_code=$?
        echo "$output"
    else
        output=$(zsh "$test_path" 2>&1)
        exit_code=$?
    fi

    # Parse results
    local passed failed skipped total
    passed=$(echo "$output" | grep "Passed:" | awk '{print $2}' | head -1)
    failed=$(echo "$output" | grep "Failed:" | awk '{print $2}' | head -1)
    skipped=$(echo "$output" | grep "Skipped:" | awk '{print $2}' | head -1)
    total=$(echo "$output" | grep "^Total:" | awk '{print $2}' | head -1)

    # Default to 0 if not found
    passed=${passed:-0}
    failed=${failed:-0}
    skipped=${skipped:-0}
    total=${total:-0}

    # Store results
    TEST_RESULTS[$suite_id]="$passed|$failed|$skipped|$total|$exit_code"

    # Update totals
    ((TOTAL_PASSED += passed))
    ((TOTAL_FAILED += failed))
    ((TOTAL_SKIPPED += skipped))
    ((TOTAL_TESTS += total))
    ((TOTAL_RUN += 1))

    # Print summary line
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ $suite_name: PASSED${RESET} ($passed passed, $failed failed, $skipped skipped)"
    else
        echo -e "${RED}✗ $suite_name: FAILED${RESET} ($passed passed, $failed failed, $skipped skipped)"
    fi

    return $exit_code
}

run_all_tests() {
    local overall_success=true

    for suite_spec in "${TEST_SUITES[@]}"; do
        local suite_name="${suite_spec%:*}"
        local suite_id="${suite_spec#*:}"

        local test_file
        case "$suite_id" in
            bug-fix-validation)
                test_file="bug-fix-validation.test.sh"
                ;;
            vm-common)
                test_file="unit/vm-common.test.sh"
                ;;
            vde-shell-compat)
                test_file="unit/vde-shell-compat.test.sh"
                ;;
            vde-parser)
                test_file="unit/vde-parser.test.sh"
                ;;
            vm-lifecycle)
                test_file="integration/vm-lifecycle-integration.test.sh"
                ;;
            *)
                test_file="$suite_id"
                ;;
        esac

        if ! run_test_suite "$suite_name" "$suite_id" "$test_file"; then
            overall_success=false
        fi
    done

    return $overall_success
}

# =============================================================================
# REPORTING
# =============================================================================

print_summary() {
    echo ""
    echo -e "${BOLD}========================================"
    echo "Test Suite Summary"
    echo -e "========================================${RESET}"
    echo ""

    # Test suite breakdown
    echo -e "${BOLD}Test Suites:${RESET}"
    for suite_spec in "${TEST_SUITES[@]}"; do
        local suite_name="${suite_spec%:*}"
        local suite_id="${suite_spec#*:}"

        local result="${TEST_RESULTS[$suite_id]}"
        local passed="${result%%|*}"
        local rest="${result#*|}"
        local failed="${rest%%|*}"
        rest="${rest#*|}"
        local skipped="${rest%%|*}"
        rest="${rest#*|}"
        local total="${rest%%|*}"
        local exit_code="${rest##*|}"

        if [[ $exit_code -eq 0 ]]; then
            echo -e "  ${GREEN}✓${RESET} $suite_name"
        else
            echo -e "  ${RED}✗${RESET} $suite_name"
        fi
        echo "     Passed: $passed, Failed: $failed, Skipped: $skipped, Total: $total"
    done

    echo ""
    echo -e "${BOLD}Overall Results:${RESET}"
    echo -e "  Test Suites Run:  ${CYAN}$TOTAL_RUN${RESET}"
    echo -e "  Total Tests:      ${CYAN}$TOTAL_TESTS${RESET}"
    echo -e "  ${GREEN}Passed:${RESET}           $TOTAL_PASSED"
    echo -e "  ${RED}Failed:${RESET}           $TOTAL_FAILED"
    echo -e "  ${YELLOW}Skipped:${RESET}          $TOTAL_SKIPPED"

    echo ""
    local pass_rate=0
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        pass_rate=$((TOTAL_PASSED * 100 / TOTAL_TESTS))
    fi

    if [[ $TOTAL_FAILED -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}All tests passed!${RESET} (Pass rate: ${pass_rate}%)"
        echo ""
        return 0
    else
        echo -e "${RED}${BOLD}Some tests failed!${RESET} (Pass rate: ${pass_rate}%)"
        echo ""
        return 1
    fi
}

# =============================================================================
# PARALLEL EXECUTION (Experimental)
# =============================================================================

run_tests_parallel() {
    echo -e "${YELLOW}Parallel execution is experimental${RESET}"
    echo ""

    local pids=()

    for suite_spec in "${TEST_SUITES[@]}"; do
        local suite_name="${suite_spec%:*}"
        local suite_id="${suite_spec#*:}"

        local test_file
        case "$suite_id" in
            bug-fix-validation)
                test_file="bug-fix-validation.test.sh"
                ;;
            vm-common)
                test_file="unit/vm-common.test.sh"
                ;;
            vde-shell-compat)
                test_file="unit/vde-shell-compat.test.sh"
                ;;
            vde-parser)
                test_file="unit/vde-parser.test.sh"
                ;;
            vm-lifecycle)
                test_file="integration/vm-lifecycle-integration.test.sh"
                ;;
            *)
                test_file="$suite_id"
                ;;
        esac

        echo "Starting $suite_name..."
        zsh "$SCRIPT_DIR/$test_file" > "/tmp/vde-test-${suite_id}.log" 2>&1 &
        pids+=($!)
    done

    # Wait for all tests
    for i in {1..${#pids[@]}}; do
        wait ${pids[$i]}
    done

    # Collect results
    for suite_spec in "${TEST_SUITES[@]}"; do
        local suite_id="${suite_spec#*:}"
        local log_file="/tmp/vde-test-${suite_id}.log"

        if [[ -f "$log_file" ]]; then
            cat "$log_file"
            rm -f "$log_file"
        fi
    done
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    local test_selector="$TEST_SELECTOR"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -p|--parallel)
                PARALLEL=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            --list)
                list_tests
                exit 0
                ;;
            -*)
                echo -e "${RED}Error: Unknown option: $1${RESET}"
                echo ""
                show_usage
                exit 1
                ;;
            *)
                test_selector="$1"
                shift
                ;;
        esac
    done

    # Discover tests
    discover_tests "$test_selector"

    # Print header
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════${RESET}"
    echo -e "${BOLD}    VDE Test Suite${RESET}"
    echo -e "${BOLD}══════════════════════════════════════════════════${RESET}"
    echo ""
    echo "Selector: $test_selector"
    echo "Verbose:  $VERBOSE"
    echo "Parallel: $PARALLEL"
    echo ""

    # Run tests
    local exit_code
    if [[ "$PARALLEL" == "true" ]]; then
        run_tests_parallel
        exit_code=$?
    else
        run_all_tests
        exit_code=$?
    fi

    # Print summary
    print_summary
    exit $exit_code
}

# Run main
main "$@"
