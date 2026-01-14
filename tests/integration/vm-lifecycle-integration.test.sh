#!/usr/bin/env zsh
# Integration Tests for VM Lifecycle
# Tests end-to-end VM creation, startup, and management workflows

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source VDE libraries
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vm-common"

# Test configuration
VERBOSE=${VERBOSE:-false}
TESTS_PASSED=0
TESTS_FAILED=0
TEST_VM_PREFIX="test-integration-$$"

# Colors
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    CYAN='\033[0;36m'
    RESET='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    CYAN=''
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

info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${CYAN}[INFO]${RESET} $*"
    fi
}

# Cleanup function
cleanup() {
    info "Cleaning up test VMs..."
    for vm in $(get_all_vms 2>/dev/null | grep "$TEST_VM_PREFIX"); do
        info "Removing test VM: $vm"
        # Try to stop the VM if running
        shutdown-virtual "$vm" >/dev/null 2>&1 || true
        # Remove the VM directory
        rm -rf "$CONFIGS_DIR/$vm"
    done
}

trap cleanup EXIT INT TERM

# =============================================================================
# TESTS: VM Type Discovery
# =============================================================================

test_vm_types_loadable() {
    test_start "VM types can be loaded"

    if load_vm_types --no-cache; then
        local count
        count=$(get_all_vms | wc -w)
        if [[ $count -gt 0 ]]; then
            test_pass "VM types can be loaded ($count types)"
            return
        fi
    fi

    test_fail "VM types" "failed to load or no VM types found"
}

test_vm_types_have_required_fields() {
    test_start "VM types have required fields"

    local vm="python"
    local type display install

    type=$(get_vm_info type "$vm")
    display=$(get_vm_info display "$vm")
    install=$(get_vm_info install "$vm")

    if [[ -n "$type" ]] && [[ -n "$display" ]] && [[ -n "$install" ]]; then
        test_pass "VM types have required fields"
        return
    fi

    test_fail "VM types fields" "missing fields - type:$type display:$display install:$install"
}

# =============================================================================
# TESTS: Port Allocation
# =============================================================================

test_port_allocation_basic() {
    test_start "Port allocation (basic)"

    # Use a test range that won't conflict
    local test_start_port=2900
    local test_end_port=2910

    local port
    port=$(find_next_available_port "$test_start_port" "$test_end_port")

    if [[ -n "$port" ]] && [[ $port -ge $test_start_port ]] && [[ $port -le $test_end_port ]]; then
        test_pass "Port allocation (basic - allocated $port)"
        return
    fi

    test_fail "Port allocation" "no port allocated or out of range"
}

test_port_allocation_sequence() {
    test_start "Port allocation (sequential)"

    local test_start_port=2900
    local test_end_port=2910

    local port1 port2
    port1=$(find_next_available_port "$test_start_port" "$test_end_port")

    # Simulate port being taken by adding to registry
    _assoc_set "PORT_REGISTRY" "test-vm-1" "$port1"

    port2=$(find_next_available_port "$test_start_port" "$test_end_port")

    if [[ $port2 -gt $port1 ]]; then
        test_pass "Port allocation (sequential - $port1, $port2)"
        _assoc_clear "PORT_REGISTRY"
        return
    fi

    test_fail "Port allocation" "ports not sequential: $port1, $port2"
    _assoc_clear "PORT_REGISTRY"
}

# =============================================================================
# TESTS: Template Rendering
# =============================================================================

test_template_render_language() {
    test_start "Template rendering (language VM)"

    local template="$TEMPLATES_DIR/compose-language.yml"

    if [[ ! -f "$template" ]]; then
        test_fail "Template rendering" "template not found: $template"
        return
    fi

    local rendered
    rendered=$(render_template "$template" \
        NAME "${TEST_VM_PREFIX}-testlang" \
        SSH_PORT 2900 \
        USERNAME devuser \
        UID 1000 \
        GID 1000 \
        INSTALL_CMD "echo test" \
        SSH_IDENTITY_FILE "~/.ssh/id_ed25519")

    if [[ -n "$rendered" ]]; then
        # Check that placeholders were replaced
        if [[ "$rendered" != *"{{NAME}}"* ]] && [[ "$rendered" != *"{{SSH_PORT}}"* ]]; then
            # Check that values are present
            if [[ "$rendered" == *"${TEST_VM_PREFIX}-testlang"* ]] && [[ "$rendered" == *"2900"* ]]; then
                test_pass "Template rendering (language VM)"
                return
            fi
        fi
    fi

    test_fail "Template rendering" "template not rendered correctly"
}

test_template_render_service() {
    test_start "Template rendering (service VM)"

    local template="$TEMPLATES_DIR/compose-service.yml"

    if [[ ! -f "$template" ]]; then
        test_fail "Template rendering" "template not found: $template"
        return
    fi

    local rendered
    rendered=$(render_template "$template" \
        NAME "${TEST_VM_PREFIX}-testsvc" \
        SSH_PORT 2901 \
        SVC_PORT 5432 \
        USERNAME devuser \
        UID 1000 \
        GID 1000)

    if [[ -n "$rendered" ]]; then
        if [[ "$rendered" == *"${TEST_VM_PREFIX}-testsvc"* ]] && [[ "$rendered" == *"2901"* ]]; then
            test_pass "Template rendering (service VM)"
            return
        fi
    fi

    test_fail "Template rendering" "template not rendered correctly"
}

# =============================================================================
# TESTS: Directory Structure
# =============================================================================

test_directories_exist() {
    test_start "Required directories exist"

    local required_dirs=(
        "$CONFIGS_DIR"
        "$TEMPLATES_DIR"
        "$DATA_DIR"
        "$BACKUP_DIR"
        "$PROJECT_ROOT/projects"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/env-files"
    )

    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            test_fail "Required directories" "missing: $dir"
            return
        fi
    done

    test_pass "Required directories exist"
}

# =============================================================================
# TESTS: File Operations
# =============================================================================

test_acquire_release_lock() {
    test_start "File locking (acquire/release)"

    local lock_file="/tmp/vde-test-lock-$$"

    if acquire_lock "$lock_file" 5; then
        if release_lock "$lock_file"; then
            test_pass "File locking (acquire/release)"
            return
        fi
    fi

    test_fail "File locking" "lock operation failed"
}

test_lock_exclusion() {
    test_start "File locking (mutual exclusion)"

    local lock_file="/tmp/vde-test-lock-exclude-$$"

    acquire_lock "$lock_file" 5

    # Try to acquire again in a subshell
    if (acquire_lock "$lock_file" 1); then
        test_fail "File locking" "lock should be exclusive"
        release_lock "$lock_file"
        return
    fi

    release_lock "$lock_file"
    test_pass "File locking (mutual exclusion)"
}

# =============================================================================
# TESTS: SSH Configuration
# =============================================================================

test_ssh_key_detection() {
    test_start "SSH key detection"

    local key
    key=$(get_primary_ssh_key)

    if [[ -n "$key" ]]; then
        if [[ -f "$HOME/.ssh/$key" ]] || [[ -f "$HOME/.ssh/${key}.pub" ]]; then
            test_pass "SSH key detection (found $key)"
            return
        fi
    fi

    test_fail "SSH key detection" "no SSH key found"
}

test_ssh_config_template_exists() {
    test_start "SSH config template exists"

    if [[ -f "$BACKUP_DIR/ssh/config" ]]; then
        test_pass "SSH config template exists"
        return
    fi

    test_fail "SSH config template" "not found at $BACKUP_DIR/ssh/config"
}

# =============================================================================
# TESTS: Cache System
# =============================================================================

test_cache_directory_exists() {
    test_start "Cache directory exists"

    if [[ -d "$CACHE_DIR" ]]; then
        test_pass "Cache directory exists"
        return
    fi

    test_fail "Cache directory" "not found at $CACHE_DIR"
}

test_cache_vm_types() {
    test_start "Cache VM types"

    # Clear existing cache
    rm -f "$VM_TYPES_CACHE"

    # Load VM types (should create cache)
    load_vm_types --no-cache

    if [[ -f "$VM_TYPES_CACHE" ]]; then
        test_pass "Cache VM types"
        return
    fi

    test_fail "Cache VM types" "cache file not created"
}

test_cache_invalidation() {
    test_start "Cache invalidation"

    # Create cache
    load_vm_types --no-cache

    # Get cache mtime
    local cache_mtime
    cache_mtime=$(stat -f %m "$VM_TYPES_CACHE" 2>/dev/null || stat -c %Y "$VM_TYPES_CACHE" 2>/dev/null)

    # Invalidate
    invalidate_vm_types_cache

    # Reload
    load_vm_types

    # Check cache was updated
    local new_mtime
    new_mtime=$(stat -f %m "$VM_TYPES_CACHE" 2>/dev/null || stat -c %Y "$VM_TYPES_CACHE" 2>/dev/null)

    if [[ $new_mtime -gt $cache_mtime ]]; then
        test_pass "Cache invalidation"
        return
    fi

    test_fail "Cache invalidation" "cache not updated"
}

# =============================================================================
# TESTS: VM Validation
# =============================================================================

test_validate_vm_name_valid() {
    test_start "Validate VM name (valid)"

    local valid_names=(
        "python"
        "rust123"
        "golang"
    )

    for name in "${valid_names[@]}"; do
        if ! validate_vm_name "$name"; then
            test_fail "Validate VM name" "valid name rejected: $name"
            return
        fi
    done

    test_pass "Validate VM name (valid)"
}

test_validate_vm_name_invalid() {
    test_start "Validate VM name (invalid)"

    local invalid_names=(
        "Python-VM"
        "my vm"
        "vm.with.dots"
        ""
    )

    for name in "${invalid_names[@]}"; do
        if validate_vm_name "$name"; then
            test_fail "Validate VM name" "invalid name accepted: $name"
            return
        fi
    done

    test_pass "Validate VM name (invalid)"
}

# =============================================================================
# TESTS: VM Resolution
# =============================================================================

test_resolve_vm_name_direct() {
    test_start "Resolve VM name (direct)"

    local result
    result=$(resolve_vm_name "python")

    if [[ "$result" == "python" ]]; then
        test_pass "Resolve VM name (direct)"
        return
    fi

    test_fail "Resolve VM name" "expected 'python', got '$result'"
}

test_resolve_vm_name_alias() {
    test_start "Resolve VM name (alias)"

    local result
    result=$(resolve_vm_name "py")

    if [[ "$result" == "python" ]]; then
        test_pass "Resolve VM name (alias)"
        return
    fi

    test_fail "Resolve VM name" "alias 'py' not resolved to 'python': $result"
}

test_resolve_vm_name_unknown() {
    test_start "Resolve VM name (unknown)"

    local result
    result=$(resolve_vm_name "nonexistentvmxyz" 2>&1)

    if [[ -z "$result" ]]; then
        test_pass "Resolve VM name (unknown)"
        return
    fi

    test_fail "Resolve VM name" "unknown VM should return empty"
}

# =============================================================================
# TESTS: Compose File Path
# =============================================================================

test_get_compose_file() {
    test_start "Get compose file path"

    local result
    result=$(get_compose_file "python")

    local expected="$CONFIGS_DIR/python/docker-compose.yml"

    if [[ "$result" == "$expected" ]]; then
        test_pass "Get compose file path"
        return
    fi

    test_fail "Get compose file path" "expected '$expected', got '$result'"
}

# =============================================================================
# TESTS: Constants
# =============================================================================

test_constants_defined() {
    test_start "All constants defined"

    local required_vars=(
        "VDE_SUCCESS"
        "VDE_ERR_GENERAL"
        "VDE_LANG_PORT_START"
        "VDE_LANG_PORT_END"
        "VDE_SVC_PORT_START"
        "VDE_SVC_PORT_END"
    )

    for var in "${required_vars[@]}"; do
        if [[ -z "${(P)var}" ]]; then
            test_fail "Constants" "undefined: $var"
            return
        fi
    done

    test_pass "All constants defined"
}

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "Integration Tests: VM Lifecycle"
    echo "=========================================="
    echo ""

    # VM Type Discovery
    test_vm_types_loadable
    test_vm_types_have_required_fields

    # Port Allocation
    test_port_allocation_basic
    test_port_allocation_sequence

    # Template Rendering
    test_template_render_language
    test_template_render_service

    # Directory Structure
    test_directories_exist

    # File Operations
    test_acquire_release_lock
    test_lock_exclusion

    # SSH Configuration
    test_ssh_key_detection
    test_ssh_config_template_exists

    # Cache System
    test_cache_directory_exists
    test_cache_vm_types
    test_cache_invalidation

    # VM Validation
    test_validate_vm_name_valid
    test_validate_vm_name_invalid

    # VM Resolution
    test_resolve_vm_name_direct
    test_resolve_vm_name_alias
    test_resolve_vm_name_unknown

    # Compose File Path
    test_get_compose_file

    # Constants
    test_constants_defined

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
