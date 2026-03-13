#!/usr/bin/env zsh
# Security Test: Command Injection Prevention
# Tests that VDE scripts properly reject malicious VM names and inputs

# Get the directory where this test script is located
TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
VDE_ROOT_DIR="$(cd "$TEST_DIR/../.." && pwd)"

# Source the library
source "$VDE_ROOT_DIR/lib/vm-common"

# Test infrastructure
TESTS_PASSED=0
TESTS_FAILED=0
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

test_start() { echo -e "${YELLOW}Testing: $1${RESET}" }
test_pass() { echo -e "  ${GREEN}✓ PASS: $1${RESET}"; ((TESTS_PASSED++)) }
test_fail() { echo -e "  ${RED}✗ FAIL: $1 - $2${RESET}"; ((TESTS_FAILED++)) }

# Test 1: VM name with semicolon
test_vm_name_with_semicolon() {
    test_start "VM name with semicolon injection"
    if validate_vm_name "test;rm -rf /" 2>/dev/null; then
        test_fail "semicolon" "Dangerous semicolon was accepted"
    else
        test_pass "semicolon injection blocked"
    fi
}

# Test 2: VM name with backticks
test_vm_name_with_backticks() {
    test_start "VM name with backtick injection"
    if validate_vm_name 'test`id`' 2>/dev/null; then
        test_fail "backticks" "Dangerous backticks were accepted"
    else
        test_pass "backtick injection blocked"
    fi
}

# Test 3: VM name with dollar parentheses
test_vm_name_with_dollar_paren() {
    test_start "VM name with command substitution"
    if validate_vm_name 'test$(whoami)' 2>/dev/null; then
        test_fail "dollar_paren" "Dangerous command substitution was accepted"
    else
        test_pass "command substitution blocked"
    fi
}

# Test 4: VM name with pipe
test_vm_name_with_pipe() {
    test_start "VM name with pipe injection"
    if validate_vm_name 'test|cat /etc/passwd' 2>/dev/null; then
        test_fail "pipe" "Dangerous pipe was accepted"
    else
        test_pass "pipe injection blocked"
    fi
}

# Test 5: VM name with ampersand
test_vm_name_with_ampersand() {
    test_start "VM name with ampersand injection"
    if validate_vm_name 'test && echo pwned' 2>/dev/null; then
        test_fail "ampersand" "Dangerous ampersand was accepted"
    else
        test_pass "ampersand injection blocked"
    fi
}

# Test 6: VM name with newline
test_vm_name_with_newline() {
    test_start "VM name with embedded newline"
    if validate_vm_name "test
malicious" 2>/dev/null; then
        test_fail "newline" "Embedded newline was accepted"
    else
        test_pass "newline injection blocked"
    fi
}

# Test 7: VM name with spaces
test_vm_name_with_spaces() {
    test_start "VM name with spaces"
    if validate_vm_name "test vm" 2>/dev/null; then
        test_fail "spaces" "Spaces were accepted"
    else
        test_pass "spaces blocked"
    fi
}

# Test 8: Valid VM names should be accepted
test_vm_name_valid_accepted() {
    test_start "Valid VM names acceptance"
    local valid_names=("python" "rust" "my123" "test1")
    local all_passed=true

    for name in "${valid_names[@]}"; do
        if ! validate_vm_name "$name" 2>/dev/null; then
            all_passed=false
            break
        fi
    done

    if [ "$all_passed" = "true" ]; then
        test_pass "valid names accepted"
    else
        test_fail "valid_names" "Some valid names were rejected"
    fi
}

# Test 9: VM name with slash
test_vm_name_with_slash() {
    test_start "VM name with slash"
    if validate_vm_name "test/etc" 2>/dev/null; then
        test_fail "slash" "Slash was accepted"
    else
        test_pass "slash blocked"
    fi
}

# Test 10: VM name with dots (path traversal)
test_vm_name_with_dots() {
    test_start "VM name with path traversal dots"
    if validate_vm_name "../etc" 2>/dev/null; then
        test_fail "dots" "Path traversal dots were accepted"
    else
        test_pass "path traversal blocked"
    fi
}

# Run all tests
echo "Running command injection security tests..."
echo ""

test_vm_name_with_semicolon
test_vm_name_with_backticks
test_vm_name_with_dollar_paren
test_vm_name_with_pipe
test_vm_name_with_ampersand
test_vm_name_with_newline
test_vm_name_with_spaces
test_vm_name_valid_accepted
test_vm_name_with_slash
test_vm_name_with_dots

# Summary
echo ""
echo "========================================"
echo "Command Injection Test Results:"
echo "  Passed: $TESTS_PASSED"
echo "  Failed: $TESTS_FAILED"
echo "========================================"

if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi
