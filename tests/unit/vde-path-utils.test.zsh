#!/usr/bin/env zsh
# Unit Tests for vde-path-utils Library
# Tests path conversion and normalization functions

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ensure HOME is exported (required by vde-path-utils)
export HOME="${HOME:-$(eval echo ~$(whoami))}"

# Clear any guard variables from .env that might prevent loading
unset _VDE_PATH_UTILS_LOADED 2>/dev/null

# Source dependencies
source "$PROJECT_ROOT/lib/vde-path-utils"

# Test configuration
VERBOSE=${VERBOSE:-false}
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    RESET=''
fi

test_start() {
    echo -e "${YELLOW}[TEST]${RESET} $1"
}

test_pass() {
    echo -e "${GREEN}[PASS]${RESET} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${RESET} $1: $2"
    ((TESTS_FAILED++))
}

# =============================================================================
# TESTS: vde_path_to_home_rel
# =============================================================================

test_path_to_home_rel_basic() {
    test_start "path to home rel (basic)"

    local result
    result=$(vde_path_to_home_rel "$HOME/.ssh/vde/id_ed25519" 2>/dev/null)
    if [[ "$result" == "~/.ssh/vde/id_ed25519" ]]; then
        test_pass "path to home rel (basic)"
        return
    fi

    test_fail "path to home rel basic" "expected '~/.ssh/vde/id_ed25519', got '$result'"
}

test_path_to_home_rel_root() {
    test_start "path to home rel (home dir)"

    local result
    result=$(vde_path_to_home_rel "$HOME" 2>/dev/null)
    if [[ "$result" == "~" ]]; then
        test_pass "path to home rel (home dir)"
        return
    fi

    test_fail "path to home rel root" "expected '~', got '$result'"
}

test_path_to_home_rel_empty() {
    test_start "path to home rel (empty)"

    local result
    result=$(vde_path_to_home_rel "" 2>/dev/null)
    if [[ -z "$result" ]]; then
        test_pass "path to home rel (empty)"
        return
    fi

    test_fail "path to home rel empty" "expected empty string, got '$result'"
}

test_path_to_home_rel_not_under_home() {
    test_start "path to home rel (not under home)"

    local result
    result=$(vde_path_to_home_rel "/etc/passwd" 2>/dev/null)
    if [[ "$result" == "/etc/passwd" ]]; then
        test_pass "path to home rel (not under home)"
        return
    fi

    test_fail "path to home rel not under home" "expected '/etc/passwd', got '$result'"
}

test_path_to_home_rel_deep() {
    test_start "path to home rel (deep path)"

    local result
    result=$(vde_path_to_home_rel "$HOME/.config/vde/cache" 2>/dev/null)
    if [[ "$result" == "~/.config/vde/cache" ]]; then
        test_pass "path to home rel (deep path)"
        return
    fi

    test_fail "path to home rel deep" "expected '~/.config/vde/cache', got '$result'"
}

# =============================================================================
# TESTS: vde_path_from_home_rel
# =============================================================================

test_path_from_home_rel_basic() {
    test_start "path from home rel (basic)"

    local result
    result=$(vde_path_from_home_rel "~/.ssh/vde/id_ed25519" 2>/dev/null)
    if [[ "$result" == "$HOME/.ssh/vde/id_ed25519" ]]; then
        test_pass "path from home rel (basic)"
        return
    fi

    test_fail "path from home rel basic" "expected '$HOME/.ssh/vde/id_ed25519', got '$result'"
}

test_path_from_home_rel_root() {
    test_start "path from home rel (tilde only)"

    local result
    result=$(vde_path_from_home_rel "~" 2>/dev/null)
    if [[ "$result" == "$HOME" ]]; then
        test_pass "path from home rel (tilde only)"
        return
    fi

    test_fail "path from home rel root" "expected '$HOME', got '$result'"
}

test_path_from_home_rel_empty() {
    test_start "path from home rel (empty)"

    local result
    result=$(vde_path_from_home_rel "" 2>/dev/null)
    if [[ -z "$result" ]]; then
        test_pass "path from home rel (empty)"
        return
    fi

    test_fail "path from home rel empty" "expected empty string, got '$result'"
}

test_path_from_home_rel_already_absolute() {
    test_start "path from home rel (already absolute)"

    local result
    result=$(vde_path_from_home_rel "/etc/passwd" 2>/dev/null)
    if [[ "$result" == "/etc/passwd" ]]; then
        test_pass "path from home rel (already absolute)"
        return
    fi

    test_fail "path from home rel absolute" "expected '/etc/passwd', got '$result'"
}

# =============================================================================
# TESTS: vde_path_normalize
# =============================================================================

test_path_normalize_basic() {
    test_start "path normalize (basic)"

    local result
    result=$(vde_path_normalize "/home/user/file" 2>/dev/null)
    if [[ "$result" == "/home/user/file" ]]; then
        test_pass "path normalize (basic)"
        return
    fi

    test_fail "path normalize basic" "expected '/home/user/file', got '$result'"
}

test_path_normalize_double_slashes() {
    test_start "path normalize (double slashes)"

    local result
    result=$(vde_path_normalize "/home//user//file" 2>/dev/null)
    if [[ "$result" == "/home/user/file" ]]; then
        test_pass "path normalize (double slashes)"
        return
    fi

    test_fail "path normalize double slashes" "expected '/home/user/file', got '$result'"
}

test_path_normalize_dot() {
    test_start "path normalize (dot)"

    local result
    result=$(vde_path_normalize "/home/./user/./file" 2>/dev/null)
    if [[ "$result" == "/home/user/file" ]]; then
        test_pass "path normalize (dot)"
        return
    fi

    test_fail "path normalize dot" "expected '/home/user/file', got '$result'"
}

test_path_normalize_empty() {
    test_start "path normalize (empty)"

    local result
    result=$(vde_path_normalize "" 2>/dev/null)
    if [[ -z "$result" ]]; then
        test_pass "path normalize (empty)"
        return
    fi

    test_fail "path normalize empty" "expected empty string, got '$result'"
}

# =============================================================================
# TESTS: vde_get_project_name
# =============================================================================

test_get_project_name() {
    test_start "get project name"

    local result
    result=$(vde_get_project_name 2>/dev/null)
    if [[ -n "$result" && "$result" != "VDE_ROOT_DIR" ]]; then
        test_pass "get project name"
        return
    fi

    test_fail "get project name" "expected non-empty project name, got '$result'"
}

# =============================================================================
# TESTS: vde_is_home_path
# =============================================================================

test_is_home_path_true() {
    test_start "is home path (true)"

    if vde_is_home_path "$HOME/.ssh" 2>/dev/null; then
        test_pass "is home path (true)"
        return
    fi

    test_fail "is home path true" "expected true for path under HOME"
}

test_is_home_path_false() {
    test_start "is home path (false)"

    if ! vde_is_home_path "/etc/passwd" 2>/dev/null; then
        test_pass "is home path (false)"
        return
    fi

    test_fail "is home path false" "expected false for path not under HOME"
}

test_is_home_path_empty() {
    test_start "is home path (empty)"

    if ! vde_is_home_path "" 2>/dev/null; then
        test_pass "is home path (empty)"
        return
    fi

    test_fail "is home path empty" "expected false for empty path"
}

# =============================================================================
# TESTS: Round-trip Conversions
# =============================================================================

test_roundtrip_home_rel() {
    test_start "round-trip (home rel -> abs -> home rel)"

    local original="~/.config/vde/cache"
    local abs_path
    abs_path=$(vde_path_from_home_rel "$original" 2>/dev/null)
    local back_to_rel
    back_to_rel=$(vde_path_to_home_rel "$abs_path" 2>/dev/null)

    # The round-trip should preserve the path portion
    if [[ "$back_to_rel" == *".config/vde/cache" ]]; then
        test_pass "round-trip (home rel -> abs -> home rel)"
        return
    fi

    test_fail "round-trip home rel" "expected path ending in '.config/vde/cache', got '$back_to_rel'"
}

# =============================================================================
# Run All Tests
# =============================================================================

echo "=============================================="
echo "VDE Path Utils Unit Tests"
echo "=============================================="

# vde_path_to_home_rel tests
test_path_to_home_rel_basic
test_path_to_home_rel_root
test_path_to_home_rel_empty
test_path_to_home_rel_not_under_home
test_path_to_home_rel_deep

# vde_path_from_home_rel tests
test_path_from_home_rel_basic
test_path_from_home_rel_root
test_path_from_home_rel_empty
test_path_from_home_rel_already_absolute

# vde_path_normalize tests
test_path_normalize_basic
test_path_normalize_double_slashes
test_path_normalize_dot
test_path_normalize_empty

# vde_get_project_name test
test_get_project_name

# vde_is_home_path tests
test_is_home_path_true
test_is_home_path_false
test_is_home_path_empty

# Round-trip tests
test_roundtrip_home_rel

echo ""
echo "=============================================="
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "=============================================="

exit $TESTS_FAILED
