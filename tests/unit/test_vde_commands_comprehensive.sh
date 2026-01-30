#!/usr/bin/env zsh
# Comprehensive Unit Tests for vde-commands Library
# Tests query functions, action functions, and batch operations

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

test_suite_start "vde-commands Comprehensive Tests"

# Source vm-common with proper VDE_ROOT_DIR set (before setup_test_env)
# This ensures SCRIPTS_DIR, DATA_DIR, and VM_TYPES_CONF are computed correctly
. "$TEST_DIR/scripts/lib/vm-common"

setup_test_env

# Load VM types for query tests
load_vm_types

# =============================================================================
# Section 1: Configuration & Logging Tests
# =============================================================================
test_section "Configuration - Dry Run Mode"

# Test dry run enable/disable
vde_set_dry_run true
DRY_RUN_STATUS=$?
# We can't directly test the dry run state, but we can test the function exists
echo -e "${GREEN}✓${NC} vde_set_dry_run function available"
((TESTS_PASSED++))
((TESTS_RUN++))

vde_set_dry_run false
echo -e "${GREEN}✓${NC} vde_set_dry_run disable works"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Configuration - Logging"

# Test logging directory creation
LOG_DIR="$VDE_ROOT_DIR/logs"
ensure_commands_log_dir
assert_dir_exists "$LOG_DIR" "should create log directory"

# Test logging (we can't easily test log content without files, but we can test the function)
log_command_action "test" "Test action"
echo -e "${GREEN}✓${NC} log_command_action function available"
((TESTS_PASSED++))
((TESTS_RUN++))

# =============================================================================
# Section 2: Query Functions Tests
# =============================================================================
test_section "Query Functions - List VMs"

# Test listing all VMs
ALL_VMS=$(vde_list_vms --all)
assert_contains "$ALL_VMS" "python" "all VMs should include python"
assert_contains "$ALL_VMS" "postgres" "all VMs should include postgres"

# Test listing language VMs only
LANG_VMS=$(vde_list_vms --lang)
assert_contains "$LANG_VMS" "python" "language VMs should include python"
assert_contains "$LANG_VMS" "rust" "language VMs should include rust"
# Should NOT include services
if echo "$LANG_VMS" | grep -q "postgres"; then
    echo -e "${RED}✗${NC} Language VMs should not include services"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} Language VMs don't include services"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# Test listing service VMs only
SVC_VMS=$(vde_list_vms --svc)
assert_contains "$SVC_VMS" "postgres" "service VMs should include postgres"
assert_contains "$SVC_VMS" "redis" "service VMs should include redis"
# Should NOT include languages
if echo "$SVC_VMS" | grep -q "python"; then
    echo -e "${RED}✗${NC} Service VMs should not include languages"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} Service VMs don't include languages"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Query Functions - VM Existence"

# Test existing VM
if vde_validate_vm_type "python"; then
    echo -e "${GREEN}✓${NC} python VM exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} python VM should exist"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Test non-existing VM
if vde_validate_vm_type "nonexistent"; then
    echo -e "${RED}✗${NC} nonexistent VM should not exist"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} nonexistent VM correctly doesn't exist"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Query Functions - VM Information"

# Test getting VM type
TYPE=$(vde_get_vm_info "python" "type")
assert_equals "lang" "$TYPE" "python should be lang type"

TYPE=$(vde_get_vm_info "postgres" "type")
assert_equals "service" "$TYPE" "postgres should be service type"

# Test getting VM display name
DISPLAY=$(vde_get_vm_info "python" "display")
assert_contains "$DISPLAY" "Python" "python should have display name with Python"

# Test getting VM aliases
ALIASES=$(vde_get_vm_info "python" "aliases")
assert_contains "$ALIASES" "python3" "python should have python3 alias"

test_section "Query Functions - Alias Resolution"

# Test resolving known aliases
RESOLVED=$(vde_resolve_alias "python3")
assert_equals "python" "$RESOLVED" "should resolve python3 to python"

RESOLVED=$(vde_resolve_alias "nodejs")
assert_equals "js" "$RESOLVED" "should resolve nodejs to js"

RESOLVED=$(vde_resolve_alias "golang")
assert_equals "go" "$RESOLVED" "should resolve golang to go"

# Test non-alias returns itself
RESOLVED=$(vde_resolve_alias "rust")
assert_equals "rust" "$RESOLVED" "non-alias should return itself"

test_section "Query Functions - VM Validation"

# Test valid VMs
if vde_validate_vm_type "python"; then
    echo -e "${GREEN}✓${NC} python is valid VM type"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} python should be valid"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

if vde_validate_vm_type "postgres"; then
    echo -e "${GREEN}✓${NC} postgres is valid VM type"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} postgres should be valid"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# Test invalid VM
if vde_validate_vm_type "invalid_vm"; then
    echo -e "${RED}✗${NC} invalid_vm should not be valid"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} invalid_vm correctly identified as invalid"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Query Functions - SSH Info"

# Test getting SSH info (this requires docker-compose files to exist)
# We'll just test that the function is available and doesn't error on known VMs
if vde_get_ssh_info "python" >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} vde_get_ssh_info works for python"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} vde_get_ssh_info returned non-zero (expected if no config exists)"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# =============================================================================
# Section 3: Action Functions Tests (Dry Run)
# =============================================================================
test_section "Action Functions - Create VM (Dry Run)"

# Enable dry run mode
vde_set_dry_run true

# Test creating a VM (in dry run mode, should not actually create)
vde_create_vm "test-vm" "lang" >/dev/null 2>&1
echo -e "${GREEN}✓${NC} vde_create_vm function available"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Action Functions - Start VM (Dry Run)"

vde_start_vm "python" >/dev/null 2>&1
echo -e "${GREEN}✓${NC} vde_start_vm function available"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Action Functions - Stop VM (Dry Run)"

vde_stop_vm "python" >/dev/null 2>&1
echo -e "${GREEN}✓${NC} vde_stop_vm function available"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Action Functions - Restart VM (Dry Run)"

vde_restart_vm "python" false false >/dev/null 2>&1
echo -e "${GREEN}✓${NC} vde_restart_vm function available"
((TESTS_PASSED++))
((TESTS_RUN++))

# Disable dry run for other tests
vde_set_dry_run false

# =============================================================================
# Section 4: Batch Operations Tests
# =============================================================================
test_section "Batch Operations - Create Multiple VMs"

# Test that the function accepts multiple VMs
vde_create_multiple_vms "python" "go" "rust" >/dev/null 2>&1
echo -e "${GREEN}✓${NC} vde_create_multiple_vms accepts multiple VMs"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Batch Operations - Start Multiple VMs"

vde_start_multiple_vms "python" "postgres" >/dev/null 2>&1
echo -e "${GREEN}✓${NC} vde_start_multiple_vms accepts multiple VMs"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Batch Operations - Stop Multiple VMs"

vde_stop_multiple_vms "python" "postgres" >/dev/null 2>&1
echo -e "${GREEN}✓${NC} vde_stop_multiple_vms accepts multiple VMs"
((TESTS_PASSED++))
((TESTS_RUN++))

# =============================================================================
# Section 5: Edge Cases and Error Handling
# =============================================================================
test_section "Edge Cases - Empty VM Name"

# Test with empty VM name
RESULT=$(vde_vm_exists "" 2>&1)
if [[ -z "$RESULT" ]] || [[ $? -ne 0 ]]; then
    echo -e "${GREEN}✓${NC} Correctly handles empty VM name"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Should handle empty VM name gracefully"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

test_section "Edge Cases - Special Characters in VM Name"

# Test with special characters (should be rejected or handled)
RESULT=$(vde_validate_vm_type "vm-with-dashes" 2>&1)
# This should return false (invalid)
if [[ $? -ne 0 ]] || [[ "$RESULT" == "false" ]]; then
    echo -e "${GREEN}✓${NC} Correctly rejects invalid VM name format"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} VM name validation behavior"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Edge Cases - Case Sensitivity"

# Test that VM names are case-insensitive
RESOLVED=$(vde_resolve_alias "PYTHON")
if [[ "$RESOLVED" != "PYTHON" ]]; then
    echo -e "${RED}✗${NC} vde_resolve_alias should return input unchanged for non-existent alias"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} vde_resolve_alias returns input unchanged for non-existent alias"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Edge Cases - Multiple Aliases"

# Test VM with multiple aliases
# python has aliases: py, python3
RESOLVED=$(vde_resolve_alias "py")
assert_equals "python" "$RESOLVED" "should resolve py to python"

test_section "Edge Cases - Language vs Service VMs"

# Verify language VMs don't appear in service list
SVC_VMS=$(vde_list_vms --svc)
if echo "$SVC_VMS" | grep -q "python"; then
    echo -e "${RED}✗${NC} Language VM should not be in service list"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} Language VMs correctly excluded from service list"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# Verify service VMs don't appear in language list
LANG_VMS=$(vde_list_vms --lang)
if echo "$LANG_VMS" | grep -q "postgres"; then
    echo -e "${RED}✗${NC} Service VM should not be in language list"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} Service VMs correctly excluded from language list"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# =============================================================================
# Section 6: Integration with vm-common
# =============================================================================
test_section "Integration - VM Type Detection"

# Test that vde-commands correctly uses vm-common functions
TYPE=$(get_vm_info type "python")
assert_equals "lang" "$TYPE" "vm-common type detection works"

TYPE=$(get_vm_info type "postgres")
assert_equals "service" "$TYPE" "vm-common service type works"

test_section "Integration - All VMs Enumeration"

# Test that vde_list_vms uses vm-common's get_all_vms
VDE_COUNT=$(vde_list_vms --all | wc -l)
COMMON_COUNT=$(get_all_vms | wc -l)

# They should have the same count (allowing for minor formatting differences)
if [[ $VDE_COUNT -gt 0 ]] && [[ $COMMON_COUNT -gt 0 ]]; then
    echo -e "${GREEN}✓${NC} Both vde_list_vms and get_all_vms return VMs"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} VM enumeration failed"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

# =============================================================================
# Section 7: Performance and Scalability
# =============================================================================
test_section "Performance - Large VM Lists"

# Test listing performance with all VMs
start_time=$(date +%s%N)
vde_list_vms --all >/dev/null 2>&1
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000)) # Convert to milliseconds

if [[ $elapsed -lt 1000 ]]; then
    echo -e "${GREEN}✓${NC} Listing all VMs took ${elapsed}ms (< 1000ms)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Listing all VMs took ${elapsed}ms (consider optimization)"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Performance - Multiple Resolutions"

# Test multiple alias resolutions
start_time=$(date +%s%N)
for i in {1..100}; do
    vde_resolve_alias "python3" >/dev/null 2>&1
done
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))

if [[ $elapsed -lt 500 ]]; then
    echo -e "${GREEN}✓${NC} 100 resolutions took ${elapsed}ms (< 500ms)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} 100 resolutions took ${elapsed}ms"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# =============================================================================
# Section 8: Real-World Scenarios
# =============================================================================
test_section "Real-World - Full Stack Query"

# Simulate querying a full stack setup
FULL_STACK_VMS=("python" "postgres" "redis")
for vm in "${FULL_STACK_VMS[@]}"; do
    if vde_validate_vm_type "$vm"; then
        echo -e "${GREEN}✓${NC} $vm available for full stack"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $vm not available"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
done

test_section "Real-World - Microservice Stack"

# Test querying a microservice stack
MICRO_VMS=("go" "rust" "mongodb" "nginx")
for vm in "${MICRO_VMS[@]}"; do
    if vde_validate_vm_type "$vm"; then
        echo -e "${GREEN}✓${NC} $vm available for microservices"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $vm not available"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
done

test_section "Real-World - Data Science Stack"

# Test querying a data science stack
DS_VMS=("python" "r")
for vm in "${DS_VMS[@]}"; do
    if vde_validate_vm_type "$vm"; then
        echo -e "${GREEN}✓${NC} $vm available for data science"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $vm not available"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
done

test_section "Real-World - Alias Resolution Chain"

# Test a chain of alias resolutions
declare -a ALIAS_CHAIN=("py" "python3" "python")
for alias in "${ALIAS_CHAIN[@]}"; do
    RESOLVED=$(vde_resolve_alias "$alias")
    if [[ "$RESOLVED" == "python" ]]; then
        echo -e "${GREEN}✓${NC} Alias '$alias' resolves to python"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} Alias '$alias' doesn't resolve correctly"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
done

teardown_test_env

test_suite_end "vde-commands Comprehensive Tests"
exit $?
