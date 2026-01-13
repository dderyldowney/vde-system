#!/usr/bin/env zsh
# Comprehensive Unit Tests for vde-parser Library
# Tests intent detection, entity extraction, and plan generation

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

test_suite_start "vde-parser Comprehensive Tests"

setup_test_env

# =============================================================================
# Section 1: Intent Detection Tests
# =============================================================================
test_section "Intent Detection - List VMs Intent"

# Test various ways users might ask to list VMs
declare -a LIST_VMS_INPUTS=(
    "what VMs can I create?"
    "list vms"
    "show available vms"
    "what vms are available?"
    "which vms can I create?"
    "show me all vms"
)

for input in "${LIST_VMS_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_LIST_VMS" "$intent" "list_vms intent for: $input"
done

test_section "Intent Detection - Create VM Intent"

declare -a CREATE_VM_INPUTS=(
    "create a Go VM"
    "create new Python environment"
    "make a Rust VM"
    "make new JavaScript container"
    "set up a PostgreSQL VM"
    "create C# environment"
)

for input in "${CREATE_VM_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_CREATE_VM" "$intent" "create_vm intent for: $input"
done

test_section "Intent Detection - Start VM Intent"

declare -a START_VM_INPUTS=(
    "start python"
    "launch golang"
    "boot rust"
    "start the postgres container"
)

for input in "${START_VM_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_START_VM" "$intent" "start_vm intent for: $input"
done

test_section "Intent Detection - Stop VM Intent"

declare -a STOP_VM_INPUTS=(
    "stop postgres"
    "shutdown redis"
    "kill nginx"
    "stop the mongodb container"
)

for input in "${STOP_VM_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_STOP_VM" "$intent" "stop_vm intent for: $input"
done

test_section "Intent Detection - Restart VM Intent"

# Must test BEFORE start/stop since restart contains "start"
declare -a RESTART_VM_INPUTS=(
    "restart rust"
    "reboot python"
    "rebuild golang"
)

for input in "${RESTART_VM_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_RESTART_VM" "$intent" "restart_vm intent for: $input"
done

test_section "Intent Detection - Status Intent"

declare -a STATUS_INPUTS=(
    "what's running?"
    "show status"
    "current state"
    "running containers"
    "status of all vms"
)

for input in "${STATUS_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_STATUS" "$intent" "status intent for: $input"
done

test_section "Intent Detection - Connect Intent"

declare -a CONNECT_INPUTS=(
    "how do I connect to Python?"
    "ssh into golang"
    "connect to rust container"
    "how do I ssh into postgres?"
)

for input in "${CONNECT_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_CONNECT" "$intent" "connect intent for: $input"
done

test_section "Intent Detection - Help Intent"

declare -a HELP_INPUTS=(
    "help"
    "what can I do?"
    "how do I use this?"
    "show me help"
)

for input in "${HELP_INPUTS[@]}"; do
    intent=$(detect_intent "$input")
    assert_equals "$INTENT_HELP" "$intent" "help intent for: $input"
done

# =============================================================================
# Section 2: VM Name Extraction Tests
# =============================================================================
test_section "VM Name Extraction - Direct Matches"

# Test direct VM name matching
VMS=$(extract_vm_names "start python and go")
assert_contains "$VMS" "python" "should extract python"
assert_contains "$VMS" "go" "should extract go"

# Test case insensitivity
VMS=$(extract_vm_names "START PYTHON AND RUST")
assert_contains "$VMS" "python" "should extract python (case insensitive)"
assert_contains "$VMS" "rust" "should extract rust (case insensitive)"

test_section "VM Name Extraction - Alias Resolution"

# Test common aliases
VMS=$(extract_vm_names "start nodejs and python3")
assert_contains "$VMS" "js" "should resolve nodejs to js"
assert_contains "$VMS" "python" "should resolve python3 to python"

VMS=$(extract_vm_names "create golang container")
assert_contains "$VMS" "go" "should resolve golang to go"

test_section "VM Name Extraction - Wildcard Expansions"

# Test "all languages" expansion
VMS=$(extract_vm_names "start all languages")
assert_contains "$VMS" "python" "all languages should include python"
assert_contains "$VMS" "rust" "all languages should include rust"
assert_contains "$VMS" "go" "all languages should include go"

# Test "all services" expansion
VMS=$(extract_vm_names "start all services")
assert_contains "$VMS" "postgres" "all services should include postgres"
assert_contains "$VMS" "redis" "all services should include redis"

# Test "all" expansion (should include both languages and services)
VMS=$(extract_vm_names "start all")
assert_contains "$VMS" "python" "all should include language"
assert_contains "$VMS" "postgres" "all should include service"

test_section "VM Name Extraction - No Matches"

# Test input with no recognizable VMs
VMS=$(extract_vm_names "start something nonexistent")
if [[ -n "$VMS" ]]; then
    echo -e "${RED}✗${NC} Should return empty for non-existent VMs"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} Correctly returns empty for non-existent VMs"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# =============================================================================
# Section 3: Filter Extraction Tests
# =============================================================================
test_section "Filter Extraction - Language Filter"

FILTER=$(extract_filter "show all languages")
assert_equals "lang" "$FILTER" "should extract lang filter"

FILTER=$(extract_filter "list language vms")
assert_equals "lang" "$FILTER" "should extract lang from 'language'"

test_section "Filter Extraction - Service Filter"

FILTER=$(extract_filter "show all services")
assert_equals "svc" "$FILTER" "should extract svc filter"

FILTER=$(extract_filter "list service vms")
assert_equals "svc" "$FILTER" "should extract svc from 'service'"

test_section "Filter Extraction - Default/All Filter"

FILTER=$(extract_filter "show all vms")
assert_equals "all" "$FILTER" "should default to 'all'"

FILTER=$(extract_filter "list vms")
assert_equals "all" "$FILTER" "should default to 'all' for generic queries"

# =============================================================================
# Section 4: Flag Extraction Tests
# =============================================================================
test_section "Flag Extraction - Rebuild Flag"

# Test various ways to specify rebuild
FLAGS=$(extract_flags "rebuild python")
assert_contains "$FLAGS" "rebuild=true" "should set rebuild=true"

FLAGS=$(extract_flags "re-create golang")
assert_contains "$FLAGS" "rebuild=true" "should detect re-create as rebuild"

FLAGS=$(extract_flags "start rust")
assert_contains "$FLAGS" "rebuild=false" "should default rebuild to false"

test_section "Flag Extraction - No Cache Flag"

FLAGS=$(extract_flags "rebuild python with no cache")
assert_contains "$FLAGS" "nocache=true" "should set nocache=true"

FLAGS=$(extract_flags "start golang")
assert_contains "$FLAGS" "nocache=false" "should default nocache to false"

test_section "Flag Extraction - Combined Flags"

FLAGS=$(extract_flags "rebuild rust with no cache")
assert_contains "$FLAGS" "rebuild=true" "should set rebuild=true"
assert_contains "$FLAGS" "nocache=true" "should set nocache=true"

# =============================================================================
# Section 5: Plan Generation Tests
# =============================================================================
test_section "Plan Generation - Single VM Operations"

# Test start plan
PLAN=$(generate_plan "start python")
assert_contains "$PLAN" "INTENT:start_vm" "should have start_vm intent"
assert_contains "$PLAN" "VM:python" "should include python VM"

# Test stop plan
PLAN=$(generate_plan "stop postgres")
assert_contains "$PLAN" "INTENT:stop_vm" "should have stop_vm intent"
assert_contains "$PLAN" "VM:postgres" "should include postgres VM"

# Test restart plan
PLAN=$(generate_plan "restart rust")
assert_contains "$PLAN" "INTENT:restart_vm" "should have restart_vm intent"
assert_contains "$PLAN" "VM:rust" "should include rust VM"

test_section "Plan Generation - Multi VM Operations"

# Test multiple VMs
PLAN=$(generate_plan "start python and go")
assert_contains "$PLAN" "INTENT:start_vm" "should have start_vm intent"
assert_contains "$PLAN" "VM:" "should include VM list"
echo "$PLAN" | grep "^VM:" | grep -q "python" || { echo "Missing python in multi-VM plan"; exit 1; }
echo "$PLAN" | grep "^VM:" | grep -q "go" || { echo "Missing go in multi-VM plan"; exit 1; }
echo -e "${GREEN}✓${NC} Multi-VM plan includes both VMs"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Plan Generation - Full Stack Setup"

PLAN=$(generate_plan "create Python and PostgreSQL")
assert_contains "$PLAN" "INTENT:create_vm" "should have create_vm intent"
echo "$PLAN" | grep "^VM:" | grep -q "python" || { echo "Missing python"; exit 1; }
echo "$PLAN" | grep "^VM:" | grep -q "postgres" || { echo "Missing postgres"; exit 1; }
echo -e "${GREEN}✓${NC} Full stack plan includes both VMs"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Plan Generation - Flag Handling"

PLAN=$(generate_plan "rebuild python with no cache")
assert_contains "$PLAN" "INTENT:restart_vm" "should have restart_vm intent"
assert_contains "$PLAN" "rebuild=true" "should set rebuild flag"
assert_contains "$PLAN" "nocache=true" "should set nocache flag"

test_section "Plan Generation - Filter Handling"

PLAN=$(generate_plan "show all languages")
assert_contains "$PLAN" "INTENT:list_vms" "should have list_vms intent"
assert_contains "$PLAN" "FILTER:lang" "should set lang filter"

PLAN=$(generate_plan "list services")
assert_contains "$PLAN" "FILTER:svc" "should set svc filter"

test_section "Plan Generation - Status Query"

PLAN=$(generate_plan "what's running?")
assert_contains "$PLAN" "INTENT:status" "should have status intent"

test_section "Plan Generation - Connect Query"

PLAN=$(generate_plan "how do I connect to Python?")
assert_contains "$PLAN" "INTENT:connect" "should have connect intent"
assert_contains "$PLAN" "VM:python" "should include python VM"

test_section "Plan Generation - Help Query"

PLAN=$(generate_plan "help")
assert_contains "$PLAN" "INTENT:help" "should have help intent"

# =============================================================================
# Section 6: Edge Cases and Error Handling
# =============================================================================
test_section "Edge Cases - Empty Input"

PLAN=$(generate_plan "")
assert_contains "$PLAN" "INTENT:help" "empty input should default to help"

test_section "Edge Cases - Ambiguous Input"

PLAN=$(generate_plan "I need help")
assert_contains "$PLAN" "INTENT:help" "ambiguous input should default to help"

test_section "Edge Cases - Mixed Case Input"

VMS=$(extract_vm_names "START Python AND Go")
echo "$VMS" | grep -q "python" || { echo "Mixed case not handled"; exit 1; }
echo -e "${GREEN}✓${NC} Mixed case input handled correctly"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Edge Cases - Partial VM Names"

# Test that partial matches don't cause false positives
VMS=$(extract_vm_names "start p")
# Should not match "python" from just "p"
if echo "$VMS" | grep -q "python"; then
    echo -e "${RED}✗${NC} Should not match partial names"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓${NC} Correctly rejects partial matches"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Edge Cases - Special Characters"

PLAN=$(generate_plan "start python, go, and rust!")
assert_contains "$PLAN" "INTENT:start_vm" "should handle special characters"

# =============================================================================
# Section 7: Complex Real-World Scenarios
# =============================================================================
test_section "Real-World - Microservices Setup"

PLAN=$(generate_plan "create Python API, Go service, and postgres database")
assert_contains "$PLAN" "INTENT:create_vm" "should create multiple VMs"
echo "$PLAN" | grep "^VM:" | grep -q "python" || { echo "Missing python"; exit 1; }
echo "$PLAN" | grep "^VM:" | grep -q "go" || { echo "Missing go"; exit 1; }
echo "$PLAN" | grep "^VM:" | grep -q "postgres" || { echo "Missing postgres"; exit 1; }
echo -e "${GREEN}✓${NC} Microservices setup plan includes all VMs"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Real-World - Development Workflow"

# Simulate a typical dev workflow
PLAN=$(generate_plan "start python and postgres")
assert_contains "$PLAN" "INTENT:start_vm" "should start development stack"

PLAN=$(generate_plan "check status")
assert_contains "$PLAN" "INTENT:status" "should check status"

PLAN=$(generate_plan "how do I connect to python?")
assert_contains "$PLAN" "INTENT:connect" "should provide connection info"

test_section "Real-World - Cleanup Operations"

PLAN=$(generate_plan "stop all services")
assert_contains "$PLAN" "INTENT:stop_vm" "should stop all services"

PLAN=$(generate_plan "stop everything")
assert_contains "$PLAN" "INTENT:stop_vm" "should stop everything"

test_section "Real-World - Maintenance Operations"

PLAN=$(generate_plan "restart postgres with rebuild")
assert_contains "$PLAN" "INTENT:restart_vm" "should restart with rebuild"
assert_contains "$PLAN" "rebuild=true" "should set rebuild flag"

teardown_test_env

test_suite_end "vde-parser Comprehensive Tests"
exit $?
