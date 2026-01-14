#!/usr/bin/env zsh
# Unit Tests for vm-common Library
# Tests core VM management functions

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source the library under test
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vm-common"

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

# Test helpers
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

assert_equals() {
    local expected="$1"
    local actual="$2"
    local msg="${3:-assertion failed}"
    if [[ "$actual" == "$expected" ]]; then
        return 0
    fi
    echo "  Expected: '$expected'"
    echo "  Actual:   '$actual'"
    return 1
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    if [[ "$haystack" == *"$needle"* ]]; then
        return 0
    fi
    echo "  String '$needle' not found in '$haystack'"
    return 1
}

assert_not_empty() {
    local value="$1"
    if [[ -n "$value" ]]; then
        return 0
    fi
    echo "  Value is empty"
    return 1
}

# =============================================================================
# TESTS: VM Type Loading
# =============================================================================

test_load_vm_types() {
    test_start "load_vm_types"

    # Force reload
    load_vm_types --no-cache

    # Check that VM types are loaded
    local python_type
    python_type=$(get_vm_info type "python")
    if [[ "$python_type" == "lang" ]]; then
        test_pass "load_vm_types"
        return
    fi

    test_fail "load_vm_types" "python type not loaded correctly"
}

test_cache_vm_types() {
    test_start "cache_vm_types"

    # Clear cache first
    invalidate_vm_types_cache

    # Load VM types (should create cache)
    load_vm_types

    # Check cache exists
    if [[ -f "$VM_TYPES_CACHE" ]]; then
        test_pass "cache_vm_types"
        return
    fi

    test_fail "cache_vm_types" "cache file not created"
}

test_load_from_cache() {
    test_start "load_from_cache"

    # Ensure cache exists
    load_vm_types

    # Clear in-memory loaded flag
    _VM_TYPES_LOADED=0

    # Load from cache
    load_vm_types

    # Check that VM types are still available
    local python_type
    python_type=$(get_vm_info type "python")
    if [[ "$python_type" == "lang" ]]; then
        test_pass "load_from_cache"
        return
    fi

    test_fail "load_from_cache" "failed to load from cache"
}

# =============================================================================
# TESTS: VM Info Queries
# =============================================================================

test_get_vm_info_type() {
    test_start "get_vm_info type"

    local result
    result=$(get_vm_info type "python")

    if [[ "$result" == "lang" ]]; then
        test_pass "get_vm_info type"
        return
    fi

    test_fail "get_vm_info type" "expected 'lang', got '$result'"
}

test_get_vm_info_display() {
    test_start "get_vm_info display"

    local result
    result=$(get_vm_info display "python")

    if [[ -n "$result" ]]; then
        test_pass "get_vm_info display"
        return
    fi

    test_fail "get_vm_info display" "display name is empty"
}

test_get_vm_info_install() {
    test_start "get_vm_info install"

    local result
    result=$(get_vm_info install "python")

    if [[ -n "$result" ]]; then
        test_pass "get_vm_info install"
        return
    fi

    test_fail "get_vm_info install" "install command is empty"
}

# =============================================================================
# TESTS: VM Discovery
# =============================================================================

test_get_all_vms() {
    test_start "get_all_vms"

    local result
    result=$(get_all_vms)

    # Should contain at least some known VMs
    if echo "$result" | grep -q "python"; then
        test_pass "get_all_vms"
        return
    fi

    test_fail "get_all_vms" "python not in result"
}

test_get_lang_vms() {
    test_start "get_lang_vms"

    local result
    result=$(get_lang_vms)

    # Should contain python, rust, etc.
    if echo "$result" | grep -q "python"; then
        test_pass "get_lang_vms"
        return
    fi

    test_fail "get_lang_vms" "python not in result"
}

test_get_service_vms() {
    test_start "get_service_vms"

    local result
    result=$(get_service_vms)

    # Should contain postgres, redis, etc.
    if echo "$result" | grep -q "postgres\|redis\|mongodb"; then
        test_pass "get_service_vms"
        return
    fi

    test_fail "get_service_vms" "no service VMs found"
}

test_is_known_vm() {
    test_start "is_known_vm"

    if is_known_vm "python"; then
        test_pass "is_known_vm"
        return
    fi

    test_fail "is_known_vm" "python not recognized"
}

test_resolve_vm_name() {
    test_start "resolve_vm_name"

    local result
    result=$(resolve_vm_name "golang")

    if [[ "$result" == "go" ]]; then
        test_pass "resolve_vm_name"
        return
    fi

    test_fail "resolve_vm_name" "expected 'go', got '$result'"
}

# =============================================================================
# TESTS: Port Management
# =============================================================================

test_get_allocated_ports_empty() {
    test_start "get_allocated_ports (no ports allocated)"

    # Use a range unlikely to be in use
    local result
    result=$(get_allocated_ports 9900 9905)

    if [[ -z "$result" ]]; then
        test_pass "get_allocated_ports (no ports allocated)"
        return
    fi

    test_fail "get_allocated_ports" "unexpected ports allocated: $result"
}

test_port_range_constants() {
    test_start "port range constants"

    if [[ $VDE_LANG_PORT_START -eq 2200 ]] && \
       [[ $VDE_LANG_PORT_END -eq 2299 ]] && \
       [[ $VDE_SVC_PORT_START -eq 2400 ]] && \
       [[ $VDE_SVC_PORT_END -eq 2499 ]]; then
        test_pass "port range constants"
        return
    fi

    test_fail "port range constants" "constants don't match expected values"
}

test_acquire_release_lock() {
    test_start "acquire_release_lock"

    local test_lock="/tmp/vde-test-lock-$$"

    if acquire_lock "$test_lock" 5; then
        if release_lock "$test_lock"; then
            test_pass "acquire_release_lock"
            return
        fi
    fi

    test_fail "acquire_release_lock" "lock operation failed"
    rm -rf "${test_lock}.lock" 2>/dev/null
}

test_lock_timeout() {
    test_start "lock_timeout"

    local test_lock="/tmp/vde-test-lock-timeout-$$"

    # Acquire lock
    acquire_lock "$test_lock" 5

    # Try to acquire again with short timeout - should fail
    if ! acquire_lock "$test_lock" 1; then
        release_lock "$test_lock"
        test_pass "lock_timeout"
        return
    fi

    test_fail "lock_timeout" "lock should have timed out"
    release_lock "$test_lock"
    rm -rf "${test_lock}.lock" 2>/dev/null
}

# =============================================================================
# TESTS: Docker Compose Functions
# =============================================================================

test_get_compose_file() {
    test_start "get_compose_file"

    local result
    result=$(get_compose_file "python")

    local expected="$CONFIGS_DIR/python/docker-compose.yml"
    if [[ "$result" == "$expected" ]]; then
        test_pass "get_compose_file"
        return
    fi

    test_fail "get_compose_file" "expected '$expected', got '$result'"
}

test_build_docker_opts() {
    test_start "build_docker_opts"

    local result
    result=$(build_docker_opts true false)

    if [[ "$result" == "--build" ]]; then
        test_pass "build_docker_opts (rebuild only)"
        return
    fi

    test_fail "build_docker_opts" "expected '--build', got '$result'"
}

test_build_docker_opts_with_nocache() {
    test_start "build_docker_opts (with no-cache)"

    local result
    result=$(build_docker_opts true true)

    if [[ "$result" == "--build --no-cache" ]]; then
        test_pass "build_docker_opts (with no-cache)"
        return
    fi

    test_fail "build_docker_opts" "expected '--build --no-cache', got '$result'"
}

# =============================================================================
# TESTS: Template Rendering
# =============================================================================

test_render_template() {
    test_start "render_template"

    local test_template="/tmp/vde-test-template-$$"
    echo "Hello {{NAME}}, port is {{PORT}}" > "$test_template"

    local result
    result=$(render_template "$test_template" NAME "World" PORT "8080")

    if [[ "$result" == "Hello World, port is 8080" ]]; then
        test_pass "render_template"
        rm -f "$test_template"
        return
    fi

    test_fail "render_template" "unexpected result: '$result'"
    rm -f "$test_template"
}

test_render_template_with_special_chars() {
    test_start "render_template (special chars)"

    local test_template="/tmp/vde-test-template-chars-$$"
    echo "Path: {{PATH}}" > "$test_template"

    local result
    result=$(render_template "$test_template" PATH "/usr/local/bin:.")

    # Should handle slashes and colons
    if [[ "$result" == "Path: /usr/local/bin:." ]]; then
        test_pass "render_template (special chars)"
        rm -f "$test_template"
        return
    fi

    test_fail "render_template" "unexpected result: '$result'"
    rm -f "$test_template"
}

# =============================================================================
# TESTS: VM Existence
# =============================================================================

test_vm_exists() {
    test_start "vm_exists"

    # This test assumes python VM has been created
    # Skip gracefully if not
    if vm_exists "python"; then
        test_pass "vm_exists (python created)"
        return
    fi

    test_pass "vm_exists (python not created - skipped)"
}

test_vm_exists_negative() {
    test_start "vm_exists (non-existent VM)"

    if ! vm_exists "nonexistentvm123"; then
        test_pass "vm_exists (non-existent VM)"
        return
    fi

    test_fail "vm_exists" "non-existent VM should not exist"
}

# =============================================================================
# TESTS: Validation Functions
# =============================================================================

test_validate_vm_name_valid() {
    test_start "validate_vm_name (valid)"

    if validate_vm_name "python123"; then
        test_pass "validate_vm_name (valid)"
        return
    fi

    test_fail "validate_vm_name" "valid name rejected"
}

test_validate_vm_name_invalid_chars() {
    test_start "validate_vm_name (invalid chars)"

    if ! validate_vm_name "Python-VM"; then
        test_pass "validate_vm_name (invalid chars)"
        return
    fi

    test_fail "validate_vm_name" "invalid name should be rejected"
}

test_validate_vm_name_empty() {
    test_start "validate_vm_name (empty)"

    if ! validate_vm_name ""; then
        test_pass "validate_vm_name (empty)"
        return
    fi

    test_fail "validate_vm_name" "empty name should be rejected"
}

# =============================================================================
# TESTS: Logging Functions
# =============================================================================

test_log_info() {
    test_start "log_info"

    local result
    result=$(log_info "test message" 2>&1)

    if echo "$result" | grep -q "test message"; then
        test_pass "log_info"
        return
    fi

    test_fail "log_info" "message not in output"
}

test_log_error() {
    test_start "log_error"

    local result
    result=$(log_error "error message" 2>&1)

    if echo "$result" | grep -q "error message"; then
        test_pass "log_error"
        return
    fi

    test_fail "log_error" "message not in output"
}

# =============================================================================
# TESTS: Return Codes
# =============================================================================

test_return_code_constants() {
    test_start "return code constants"

    if [[ $VDE_SUCCESS -eq 0 ]] && \
       [[ $VDE_ERR_GENERAL -eq 1 ]] && \
       [[ $VDE_ERR_INVALID_INPUT -eq 2 ]] && \
       [[ $VDE_ERR_NOT_FOUND -eq 3 ]] && \
       [[ $VDE_ERR_PERMISSION -eq 4 ]] && \
       [[ $VDE_ERR_TIMEOUT -eq 5 ]] && \
       [[ $VDE_ERR_EXISTS -eq 6 ]] && \
       [[ $VDE_ERR_DEPENDENCY -eq 7 ]] && \
       [[ $VDE_ERR_DOCKER -eq 8 ]] && \
       [[ $VDE_ERR_LOCK -eq 9 ]]; then
        test_pass "return code constants"
        return
    fi

    test_fail "return code constants" "constants don't match expected values"
}

# =============================================================================
# TESTS: Directory Constants
# =============================================================================

test_directory_constants() {
    test_start "directory constants"

    if [[ -n "$CONFIGS_DIR" ]] && \
       [[ -n "$SCRIPTS_DIR" ]] && \
       [[ -n "$TEMPLATES_DIR" ]] && \
       [[ -n "$DATA_DIR" ]] && \
       [[ -n "$BACKUP_DIR" ]] && \
       [[ -n "$VM_TYPES_CONF" ]]; then
        test_pass "directory constants"
        return
    fi

    test_fail "directory constants" "some constants are empty"
}

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "Unit Tests: vm-common"
    echo "=========================================="
    echo ""

    # VM Type Loading
    test_load_vm_types
    test_cache_vm_types
    test_load_from_cache

    # VM Info Queries
    test_get_vm_info_type
    test_get_vm_info_display
    test_get_vm_info_install

    # VM Discovery
    test_get_all_vms
    test_get_lang_vms
    test_get_service_vms
    test_is_known_vm
    test_resolve_vm_name

    # Port Management
    test_get_allocated_ports_empty
    test_port_range_constants
    test_acquire_release_lock
    test_lock_timeout

    # Docker Compose Functions
    test_get_compose_file
    test_build_docker_opts
    test_build_docker_opts_with_nocache

    # Template Rendering
    test_render_template
    test_render_template_with_special_chars

    # VM Existence
    test_vm_exists
    test_vm_exists_negative

    # Validation Functions
    test_validate_vm_name_valid
    test_validate_vm_name_invalid_chars
    test_validate_vm_name_empty

    # Logging Functions
    test_log_info
    test_log_error

    # Return Codes
    test_return_code_constants

    # Directory Constants
    test_directory_constants

    # Print summary
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo -e "${GREEN}Passed:  $TESTS_PASSED${RESET}"
    echo -e "${RED}Failed:  $TESTS_FAILED${RESET}"
    echo ""

    local total=$((TESTS_PASSED + TESTS_FAILED))
    echo "Total:   $total"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}All tests passed!${RESET}\n"
        exit 0
    else
        echo -e "\n${RED}Some tests failed!${RESET}\n"
        exit 1
    fi
}

# Run main
main "$@"
