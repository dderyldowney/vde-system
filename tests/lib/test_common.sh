#!/usr/bin/env sh
# Common test utilities for VDE test suite
# Shell Compatibility: Works with zsh 5.0+, bash 4.0+, bash 3.x

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# Assertion Functions
# =============================================================================

# Assert two values are equal
assert_equals() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local expected="$1"
    local actual="$2"
    local message="${3:-assert_equals failed}"

    if [ "$actual" = "$expected" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        printf "${GREEN}✓${NC} %s\n" "$message"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        printf "${RED}✗${NC} %s\n" "$message"
        echo "  Expected: $expected"
        echo "  Actual: $actual"
    fi
}

# Assert haystack contains needle
assert_contains() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local haystack="$1"
    local needle="$2"
    local message="${3:-assert_contains failed}"

    case "$haystack" in
        *"$needle"*)
            TESTS_PASSED=$((TESTS_PASSED + 1))
            printf "${GREEN}✓${NC} %s\n" "$message"
            ;;
        *)
            TESTS_FAILED=$((TESTS_FAILED + 1))
            printf "${RED}✗${NC} %s\n" "$message"
            echo "  String '$needle' not found in: $haystack"
            ;;
    esac
}

# Assert command succeeded (exit code 0)
assert_success() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local exit_code="$1"
    local message="${2:-command should succeed}"

    if [ "$exit_code" -eq 0 ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        printf "${GREEN}✓${NC} %s\n" "$message"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        printf "${RED}✗${NC} %s (exit code: %s)\n" "$message" "$exit_code"
    fi
}

# Assert file exists
assert_file_exists() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local file="$1"
    local message="${2:-file should exist: $file}"

    if [ -f "$file" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        printf "${GREEN}✓${NC} %s\n" "$message"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        printf "${RED}✗${NC} %s\n" "$message"
    fi
}

# Assert directory exists
assert_dir_exists() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local dir="$1"
    local message="${2:-directory should exist: $dir}"

    if [ -d "$dir" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        printf "${GREEN}✓${NC} %s\n" "$message"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        printf "${RED}✗${NC} %s\n" "$message"
    fi
}

# =============================================================================
# Test Suite Helpers
# =============================================================================

# Start a test suite
test_suite_start() {
    local name="$1"
    echo ""
    printf "${YELLOW}Running: %s${NC}\n" "$name"
    echo "================================"
}

# End a test suite and display results
test_suite_end() {
    local name="$1"
    echo ""
    echo "================================"
    echo "Test Suite: $name"
    echo "Tests Run: $TESTS_RUN"
    printf "${GREEN}Passed: %s${NC}\n" "$TESTS_PASSED"
    if [ "$TESTS_FAILED" -gt 0 ]; then
        printf "${RED}Failed: %s${NC}\n" "$TESTS_FAILED"
    fi
    echo ""

    # Return error code if any tests failed
    [ "$TESTS_FAILED" -eq 0 ]
}

# Print a section header
test_section() {
    local name="$1"
    echo ""
    printf "${YELLOW}%s${NC}\n" "$name"
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
    if [ -f "$VDE_ROOT_DIR/scripts/data/vm-types.conf" ]; then
        cp "$VDE_ROOT_DIR/scripts/data/vm-types.conf" "$TEST_TMP_DIR/"
    fi

    # Source the libraries if VDE_ROOT_DIR is set
    if [ -n "$VDE_ROOT_DIR" ]; then
        # shellcheck source=/dev/null
        . "$VDE_ROOT_DIR/scripts/lib/vm-common" 2>/dev/null || true
        # shellcheck source=/dev/null
        . "$VDE_ROOT_DIR/scripts/lib/vde-commands" 2>/dev/null || true
        # shellcheck source=/dev/null
        . "$VDE_ROOT_DIR/scripts/lib/vde-parser" 2>/dev/null || true
    fi

    # Set trap to ensure cleanup happens even on error/exit
    trap 'teardown_test_env' EXIT INT TERM
}

# Teardown test environment
teardown_test_env() {
    # Clean up SSH agent to prevent CI hangs
    # This is critical in CI environments where SSH agent can cause jobs to hang
    # Use kill instead of ssh-agent -k which can hang waiting for input
    if [ -n "$SSH_AGENT_PID" ]; then
        kill "$SSH_AGENT_PID" >/dev/null 2>&1 || true
        unset SSH_AUTH_SOCK SSH_AGENT_PID
    fi

    # Also kill any ssh-agent processes that might be running
    pkill -9 ssh-agent >/dev/null 2>&1 || true

    # Clean up temporary directory
    if [ -n "$TEST_TMP_DIR" ] && [ -d "$TEST_TMP_DIR" ]; then
        rm -rf "$TEST_TMP_DIR"
    fi
}

# =============================================================================
# Mock Functions for Testing
# =============================================================================

# Mock get_allocated_ports for testing
get_allocated_ports_mock() {
    printf "2200\n2201\n2400\n"
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
    printf "Tests: %s | ${GREEN}Passed: %s${NC} | ${RED}Failed: %s${NC}\n" "$TESTS_RUN" "$TESTS_PASSED" "$TESTS_FAILED"
}

# Exit with error if tests failed
exit_on_test_failure() {
    if [ "$TESTS_FAILED" -gt 0 ]; then
        echo ""
        printf "${RED}Some tests failed!${NC}\n"
        exit 1
    fi
}
