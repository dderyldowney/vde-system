#!/usr/bin/env zsh
# Common test utilities for VDE test suite

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# Assertion Functions
# =============================================================================

# Assert two values are equal
assert_equals() {
    ((TESTS_RUN++))
    local expected="$1"
    local actual="$2"
    local message="${3:-assert_equals failed}"

    if [[ "$actual" == "$expected" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo "  Expected: $expected"
        echo "  Actual: $actual"
    fi
}

# Assert haystack contains needle
assert_contains() {
    ((TESTS_RUN++))
    local haystack="$1"
    local needle="$2"
    local message="${3:-assert_contains failed}"

    if [[ "$haystack" == *"$needle"* ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo "  String '$needle' not found in: $haystack"
    fi
}

# Assert command succeeded (exit code 0)
assert_success() {
    ((TESTS_RUN++))
    local exit_code="$1"
    local message="${2:-command should succeed}"

    if [[ $exit_code -eq 0 ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message (exit code: $exit_code)"
    fi
}

# Assert file exists
assert_file_exists() {
    ((TESTS_RUN++))
    local file="$1"
    local message="${2:-file should exist: $file}"

    if [[ -f "$file" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
    fi
}

# Assert directory exists
assert_dir_exists() {
    ((TESTS_RUN++))
    local dir="$1"
    local message="${2:-directory should exist: $dir}"

    if [[ -d "$dir" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
    fi
}

# =============================================================================
# Test Suite Helpers
# =============================================================================

# Start a test suite
test_suite_start() {
    local name="$1"
    echo ""
    echo -e "${YELLOW}Running: $name${NC}"
    echo "================================"
}

# End a test suite and display results
test_suite_end() {
    local name="$1"
    echo ""
    echo "================================"
    echo "Test Suite: $name"
    echo "Tests Run: $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    fi
    echo ""

    # Return error code if any tests failed
    [[ $TESTS_FAILED -eq 0 ]]
}

# Print a section header
test_section() {
    local name="$1"
    echo ""
    echo -e "${YELLOW}$name${NC}"
    echo "--------------------------------"
}

# =============================================================================
# Setup and Teardown
# =============================================================================

# Setup test environment
setup_test_env() {
    # Create temporary test directory
    TEST_TMP_DIR=$(mktemp -d)
    export TEST_TMP_DIR

    # Copy vm-types.conf to test location
    if [[ -f "$VDE_ROOT_DIR/scripts/data/vm-types.conf" ]]; then
        cp "$VDE_ROOT_DIR/scripts/data/vm-types.conf" "$TEST_TMP_DIR/"
    fi

    # Source the libraries if VDE_ROOT_DIR is set
    if [[ -n "$VDE_ROOT_DIR" ]]; then
        source "$VDE_ROOT_DIR/scripts/lib/vm-common" 2>/dev/null || true
        source "$VDE_ROOT_DIR/scripts/lib/vde-commands" 2>/dev/null || true
        source "$VDE_ROOT_DIR/scripts/lib/vde-parser" 2>/dev/null || true
    fi

    # Set trap to ensure cleanup happens even on error/exit
    trap 'teardown_test_env' EXIT INT TERM
}

# Teardown test environment
teardown_test_env() {
    # Clean up SSH agent to prevent CI hangs
    # This is critical in CI environments where SSH agent can cause jobs to hang
    # Use kill instead of ssh-agent -k which can hang waiting for input
    if [[ -n "$SSH_AGENT_PID" ]]; then
        kill "$SSH_AGENT_PID" >/dev/null 2>&1 || true
        unset SSH_AUTH_SOCK SSH_AGENT_PID
    fi

    # Also kill any ssh-agent processes that might be running
    pkill -9 ssh-agent >/dev/null 2>&1 || true

    # Clean up temporary directory
    if [[ -n "$TEST_TMP_DIR" && -d "$TEST_TMP_DIR" ]]; then
        rm -rf "$TEST_TMP_DIR"
    fi
}

# =============================================================================
# Mock Functions for Testing
# =============================================================================

# Mock get_allocated_ports for testing
get_allocated_ports_mock() {
    echo "2200\n2201\n2400"
}

# Mock AI response for testing
mock_ai_response() {
    cat <<'EOF'
{
  "intent": "create_vm",
  "entities": {
    "vms": ["python", "postgres"],
    "flags": {
      "rebuild": false,
      "nocache": false
    }
  },
  "confidence": 0.95
}
EOF
}

# =============================================================================
# Helper Functions
# =============================================================================

# Reset test counters
reset_test_counters() {
    TESTS_RUN=0
    TESTS_PASSED=0
    TESTS_FAILED=0
}

# Get test summary
get_test_summary() {
    echo "Tests: $TESTS_RUN | ${GREEN}Passed: $TESTS_PASSED${NC} | ${RED}Failed: $TESTS_FAILED${NC}"
}

# Exit with error if tests failed
exit_on_test_failure() {
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo ""
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}
