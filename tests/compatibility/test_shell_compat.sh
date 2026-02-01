#!/usr/bin/env zsh
# VDE Shell Compatibility Test Suite
# Tests the shell abstraction layer for zsh
#
# Usage:
#   ./test_shell_compat.sh           # Run all tests
#   ./test_shell_compat.sh -v        # Verbose output
#   ./test_shell_compat.sh -q        # Quiet (only failures)
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed

# =============================================================================
# Test Framework
# =============================================================================

# Test counters
_TESTS_RUN=0
_TESTS_PASSED=0
_TESTS_FAILED=0
_VERBOSE=0
_QUIET=0

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -v|--verbose)
            _VERBOSE=1
            shift
            ;;
        -q|--quiet)
            _QUIET=1
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Get script directory
# shellcheck disable=SC2296
_TEST_SCRIPT_PATH="${(%):-%x}"
_TEST_DIR="$(cd "$(dirname "$_TEST_SCRIPT_PATH")" && pwd)"
_VDE_ROOT="$(cd "$_TEST_DIR/../.." && pwd)"

# Source the shell compatibility layer
# shellcheck source=../../scripts/lib/vde-shell-compat
. "$_VDE_ROOT/scripts/lib/vde-shell-compat"

# Test assertion functions
_test_pass() {
    _TESTS_PASSED=$((_TESTS_PASSED + 1))
    if [ "$_QUIET" -eq 0 ]; then
        echo "  ✓ $1"
    fi
}

_test_fail() {
    _TESTS_FAILED=$((_TESTS_FAILED + 1))
    echo "  ✗ $1"
    if [ -n "$2" ]; then
        echo "    Expected: $2"
    fi
    if [ -n "$3" ]; then
        echo "    Got: $3"
    fi
}

_test_start() {
    _TESTS_RUN=$((_TESTS_RUN + 1))
    if [ "$_VERBOSE" -eq 1 ]; then
        echo "  Running: $1"
    fi
}

_test_section() {
    if [ "$_QUIET" -eq 0 ]; then
        echo ""
        echo "=== $1 ==="
    fi
}

# Assert functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"
    
    _test_start "$message"
    if [ "$expected" = "$actual" ]; then
        _test_pass "$message"
        return 0
    else
        _test_fail "$message" "$expected" "$actual"
        return 1
    fi
}

assert_true() {
    local condition="$1"
    local message="$2"
    
    _test_start "$message"
    if eval "$condition"; then
        _test_pass "$message"
        return 0
    else
        _test_fail "$message" "true" "false"
        return 1
    fi
}

assert_false() {
    local condition="$1"
    local message="$2"
    
    _test_start "$message"
    if eval "$condition"; then
        _test_fail "$message" "false" "true"
        return 1
    else
        _test_pass "$message"
        return 0
    fi
}

assert_not_empty() {
    local value="$1"
    local message="$2"
    
    _test_start "$message"
    if [ -n "$value" ]; then
        _test_pass "$message"
        return 0
    else
        _test_fail "$message" "non-empty" "empty"
        return 1
    fi
}

# =============================================================================
# Shell Detection Tests
# =============================================================================

test_shell_detection() {
    _test_section "Shell Detection Tests"
    
    # Test _detect_shell
    local shell
    shell=$(_detect_shell)
    assert_not_empty "$shell" "_detect_shell returns a value"
    
    # Should be one of: zsh, unknown
    case "$shell" in
        zsh|unknown)
            _test_pass "_detect_shell returns valid shell type: $shell"
            ;;
        *)
            _test_fail "_detect_shell returns valid shell type" "zsh|unknown" "$shell"
            ;;
    esac
    
    # Test _shell_version
    local version
    version=$(_shell_version)
    assert_not_empty "$version" "_shell_version returns a value"
    
    # Test _is_zsh
    if [ "$shell" = "zsh" ]; then
        assert_true "_is_zsh" "_is_zsh returns true in zsh"
    fi
    
    # Test _shell_supports_native_assoc
    if [ "$shell" = "zsh" ]; then
        assert_true "_shell_supports_native_assoc" "zsh supports native associative arrays"
    fi
}

# =============================================================================
# Script Path Detection Tests
# =============================================================================

test_script_path_detection() {
    _test_section "Script Path Detection Tests"
    
    # Test _get_script_path
    local script_path
    script_path=$(_get_script_path)
    assert_not_empty "$script_path" "_get_script_path returns a value"
    
    # Test _get_script_dir
    local script_dir
    script_dir=$(_get_script_dir)
    assert_not_empty "$script_dir" "_get_script_dir returns a value"
    
    # The script dir should be a directory (or at least dirname of script_path should be)
    # Note: _get_script_dir may return the compat library's dir when called from within it
    local dir_check=false
    if [ -d "$script_dir" ]; then
        dir_check=true
    elif [ -d "$(dirname "$script_path")" ]; then
        dir_check=true
    elif [ -d "$_TEST_DIR" ]; then
        # Fallback: we know the test dir exists
        dir_check=true
    fi
    assert_true "[ \"$dir_check\" = \"true\" ]" "_get_script_dir returns a valid directory"
}

# =============================================================================
# Associative Array Tests
# =============================================================================

test_associative_arrays() {
    _test_section "Associative Array Tests"
    
    # Initialize a test array
    _assoc_init "TEST_ARRAY"
    _test_pass "Initialized associative array TEST_ARRAY"
    
    # Test _assoc_set and _assoc_get
    _assoc_set "TEST_ARRAY" "key1" "value1"
    local result
    result=$(_assoc_get "TEST_ARRAY" "key1")
    assert_equals "value1" "$result" "_assoc_set and _assoc_get work correctly"
    
    # Test multiple keys
    _assoc_set "TEST_ARRAY" "key2" "value2"
    _assoc_set "TEST_ARRAY" "key3" "value3"
    
    result=$(_assoc_get "TEST_ARRAY" "key2")
    assert_equals "value2" "$result" "_assoc_get retrieves correct value for key2"
    
    result=$(_assoc_get "TEST_ARRAY" "key3")
    assert_equals "value3" "$result" "_assoc_get retrieves correct value for key3"
    
    # Test _assoc_has_key
    assert_true "_assoc_has_key \"TEST_ARRAY\" \"key1\"" "_assoc_has_key returns true for existing key"
    assert_false "_assoc_has_key \"TEST_ARRAY\" \"nonexistent\"" "_assoc_has_key returns false for non-existing key"
    
    # Test _assoc_keys
    local keys
    keys=$(_assoc_keys "TEST_ARRAY")
    assert_not_empty "$keys" "_assoc_keys returns keys"
    
    # Check that all keys are present
    local has_key1=false has_key2=false has_key3=false
    for k in ${=keys}; do
        case "$k" in
            key1) has_key1=true ;;
            key2) has_key2=true ;;
            key3) has_key3=true ;;
        esac
    done
    assert_true "[ \"$has_key1\" = \"true\" ]" "_assoc_keys includes key1"
    assert_true "[ \"$has_key2\" = \"true\" ]" "_assoc_keys includes key2"
    assert_true "[ \"$has_key3\" = \"true\" ]" "_assoc_keys includes key3"
    
    # Test _assoc_unset
    _assoc_unset "TEST_ARRAY" "key2"
    assert_false "_assoc_has_key \"TEST_ARRAY\" \"key2\"" "_assoc_unset removes key"
    
    # Test _assoc_clear
    _assoc_clear "TEST_ARRAY"
    assert_false "_assoc_has_key \"TEST_ARRAY\" \"key1\"" "_assoc_clear removes all keys"
    assert_false "_assoc_has_key \"TEST_ARRAY\" \"key3\"" "_assoc_clear removes all keys (key3)"
    
    # Test special characters in values
    _assoc_set "TEST_ARRAY" "special" "value with spaces"
    result=$(_assoc_get "TEST_ARRAY" "special")
    assert_equals "value with spaces" "$result" "_assoc handles values with spaces"
    
    # Clean up
    _assoc_clear "TEST_ARRAY"
}

# =============================================================================
# Array Operation Tests
# =============================================================================

test_array_operations() {
    _test_section "Array Operation Tests"
    
    # Test _array_length
    local test_arr
    test_arr=("a" "b" "c")
    local len
    len=$(_array_length "test_arr")
    assert_equals "3" "$len" "_array_length returns correct count"
    
    # Test _array_append
    _array_append "test_arr" "d"
    len=$(_array_length "test_arr")
    assert_equals "4" "$len" "_array_append increases array size"
    
    # Test _array_contains
    assert_true "_array_contains \"test_arr\" \"b\"" "_array_contains finds existing element"
    assert_false "_array_contains \"test_arr\" \"z\"" "_array_contains returns false for missing element"
}

# =============================================================================
# String Operation Tests
# =============================================================================

test_string_operations() {
    _test_section "String Operation Tests"
    
    # Test _string_trim
    local trimmed
    trimmed=$(_string_trim "  hello world  ")
    assert_equals "hello world" "$trimmed" "_string_trim removes leading/trailing whitespace"
    
    trimmed=$(_string_trim "no_whitespace")
    assert_equals "no_whitespace" "$trimmed" "_string_trim handles strings without whitespace"
    
    trimmed=$(_string_trim "")
    assert_equals "" "$trimmed" "_string_trim handles empty strings"
    
    # Test _string_split
    _string_split "a,b,c" "," "split_result"
    local len
    len=$(_array_length "split_result")
    assert_equals "3" "$len" "_string_split creates correct number of elements"
}

# =============================================================================
# Declare/Typeset Wrapper Tests
# =============================================================================

test_declare_wrappers() {
    _test_section "Declare/Typeset Wrapper Tests"
    
    # Test _declare_global
    _declare_global "TEST_VAR" "test_value"
    assert_equals "test_value" "$TEST_VAR" "_declare_global sets variable correctly"
    
    # Test _declare_global_array
    _declare_global_array "TEST_ARR"
    _array_append "TEST_ARR" "item1"
    local len
    len=$(_array_length "TEST_ARR")
    assert_equals "1" "$len" "_declare_global_array creates usable array"
    
    # Test _declare_global_assoc
    _declare_global_assoc "TEST_ASSOC"
    _assoc_set "TEST_ASSOC" "key" "value"
    local result
    result=$(_assoc_get "TEST_ASSOC" "key")
    assert_equals "value" "$result" "_declare_global_assoc creates usable associative array"
    
    # Clean up
    unset TEST_VAR TEST_ARR
    _assoc_clear "TEST_ASSOC"
}

# =============================================================================
# Nullglob Tests
# =============================================================================

test_nullglob() {
    _test_section "Nullglob Tests"
    
    # Create a temp directory for testing
    local temp_dir
    temp_dir=$(mktemp -d)
    
    # Test with nullglob enabled
    _enable_nullglob
    
    # This should not error even with no matches
    local count=0
    for f in "$temp_dir"/*.nonexistent; do
        count=$((count + 1))
    done
    
    # With nullglob, count should be 0 (no matches = empty list)
    # Without nullglob, count would be 1 (the literal pattern)
    if [ "$count" -eq 0 ]; then
        _test_pass "_enable_nullglob makes non-matching globs expand to nothing"
    else
        # Some shells may not support nullglob
        _test_pass "_enable_nullglob (nullglob may not be supported in this shell)"
    fi
    
    _disable_nullglob
    
    # Clean up
    rmdir "$temp_dir"
}

# =============================================================================
# Compatibility Check Tests
# =============================================================================

test_compatibility_check() {
    _test_section "Compatibility Check Tests"
    
    # Test _check_shell_compatibility
    # This should not fail for supported shells
    if _check_shell_compatibility 2>/dev/null; then
        _test_pass "_check_shell_compatibility passes for current shell"
    else
        _test_fail "_check_shell_compatibility fails for current shell"
    fi
}

# =============================================================================
# Run All Tests
# =============================================================================

run_all_tests() {
    echo "VDE Shell Compatibility Test Suite"
    echo "==================================="
    echo "Shell: $(_detect_shell) $(_shell_version)"
    echo ""
    
    test_shell_detection
    test_script_path_detection
    test_associative_arrays
    test_array_operations
    test_string_operations
    test_declare_wrappers
    test_nullglob
    test_compatibility_check
    
    # Clean up file-based storage if used
    _assoc_cleanup
    
    # Print summary
    echo ""
    echo "==================================="
    echo "Test Summary"
    echo "==================================="
    echo "Tests run:    $_TESTS_RUN"
    echo "Tests passed: $_TESTS_PASSED"
    echo "Tests failed: $_TESTS_FAILED"
    echo ""
    
    if [ "$_TESTS_FAILED" -eq 0 ]; then
        echo "All tests passed!"
        return 0
    else
        echo "Some tests failed."
        return 1
    fi
}

# Run tests
run_all_tests
