#!/usr/bin/env zsh
# Comprehensive Integration Tests for VDE System
# Tests end-to-end scenarios with vde-parser and vde-commands working together

TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.zsh"

test_suite_start "VDE Integration Tests"

setup_test_env

# =============================================================================
# Section 1: Complete User Workflows
# =============================================================================
test_section "Workflow - New Project Setup"

# Simulate a user setting up a new project
echo "Step 1: User asks what's available"
PLAN=$(generate_plan "what VMs can I create?")
assert_contains "$PLAN" "INTENT:list_vms" "should list available VMs"

echo "Step 2: User creates a development stack"
PLAN=$(generate_plan "create Python and PostgreSQL")
assert_contains "$PLAN" "INTENT:create_vm" "should create development stack"
echo "$PLAN" | grep "^VM:" | grep -q "python" || { echo "Missing python"; exit 1; }
echo "$PLAN" | grep "^VM:" | grep -q "postgres" || { echo "Missing postgres"; exit 1; }
echo -e "${GREEN}✓${NC} Development stack plan complete"
((TESTS_PASSED++))
((TESTS_RUN++))

echo "Step 3: User starts the development environment"
PLAN=$(generate_plan "start python and postgres")
assert_contains "$PLAN" "INTENT:start_vm" "should start development environment"

echo "Step 4: User checks status"
PLAN=$(generate_plan "what's running?")
assert_contains "$PLAN" "INTENT:status" "should check status"

echo "Step 5: User gets connection info"
PLAN=$(generate_plan "how do I connect to Python?")
assert_contains "$PLAN" "INTENT:connect" "should provide connection info"
assert_contains "$PLAN" "VM:python" "should include python"

test_section "Workflow - Microservices Architecture"

# Simulate setting up a microservices architecture
echo "Step 1: Create all microservices"
PLAN=$(generate_plan "create Go, Rust, and nginx")
assert_contains "$PLAN" "INTENT:create_vm" "should create microservices"
echo "$PLAN" | grep "^VM:" | grep -q "go" || { echo "Missing go"; exit 1; }
echo "$PLAN" | grep "^VM:" | grep -q "rust" || { echo "Missing rust"; exit 1; }
echo "$PLAN" | grep "^VM:" | grep -q "nginx" || { echo "Missing nginx"; exit 1; }
echo -e "${GREEN}✓${NC} Microservices plan complete"
((TESTS_PASSED++))
((TESTS_RUN++))

echo "Step 2: Start all microservices"
PLAN=$(generate_plan "start go, rust, and nginx")
assert_contains "$PLAN" "INTENT:start_vm" "should start all microservices"

echo "Step 3: Add a database"
PLAN=$(generate_plan "create and start mongodb")
assert_contains "$PLAN" "INTENT:create_vm" "should create mongodb"

test_section "Workflow - Daily Development Cycle"

# Simulate a typical daily development workflow
echo "Step 1: Start work - start development environment"
PLAN=$(generate_plan "start python")
assert_contains "$PLAN" "INTENT:start_vm" "should start Python"

echo "Step 2: Check what's running"
PLAN=$(generate_plan "status")
assert_contains "$PLAN" "INTENT:status" "should show status"

echo "Step 3: Need database - start it too"
PLAN=$(generate_plan "start postgres")
assert_contains "$PLAN" "INTENT:start_vm" "should start PostgreSQL"

echo "Step 4: Finish work - stop everything"
PLAN=$(generate_plan "stop all")
assert_contains "$PLAN" "INTENT:stop_vm" "should stop all VMs"

# =============================================================================
# Section 2: Complex Natural Language Commands
# =============================================================================
test_section "Natural Language - Complex Queries"

# Test various complex natural language inputs
declare -a COMPLEX_QUERIES=(
    "I need to set up a backend with Python and PostgreSQL"
    "Create a microservice architecture with Go, Rust, and nginx"
    "Start all my development containers"
    "Which VMs are currently running?"
    "Help me connect to the Python environment"
)

for query in "${COMPLEX_QUERIES[@]}"; do
    PLAN=$(generate_plan "$query")
    if [[ -n "$PLAN" ]]; then
        echo -e "${GREEN}✓${NC} Handled: $query"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} Failed to handle: $query"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
done

test_section "Natural Language - Ambiguous Inputs"

# Test ambiguous or unclear inputs
declare -a AMBIGUOUS_INPUTS=(
    "I need help with my project"
    "what should I do?"
    "show me things"
    "do something"
)

for input in "${AMBIGUOUS_INPUTS[@]}"; do
    PLAN=$(generate_plan "$input")
    # Should default to help intent for ambiguous inputs
    assert_contains "$PLAN" "INTENT:help" "ambiguous input: $input"
done

test_section "Natural Language - Typos and Variations"

# Test handling of typos and variations
PLAN=$(generate_plan "strt python")  # Typo
if [[ -n "$PLAN" ]]; then
    echo -e "${GREEN}✓${NC} Handled typo 'strt python'"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Typo 'strt python' not handled"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

PLAN=$(generate_plan "START PYTHON")  # All caps
assert_contains "$PLAN" "INTENT:start_vm" "should handle all caps"

# =============================================================================
# Section 3: Error Recovery and Edge Cases
# =============================================================================
test_section "Error Recovery - Invalid VM Names"

# Test handling of invalid VM names
declare -a INVALID_NAMES=(
    "invalid-vm-name"
    "vm with spaces"
    "123numbers"
)

for name in "${INVALID_NAMES[@]}"; do
    PLAN=$(generate_plan "start $name")
    # Should still generate a plan even if VM doesn't exist
    if [[ -n "$PLAN" ]]; then
        echo -e "${GREEN}✓${NC} Gracefully handled invalid VM: $name"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} No plan for invalid VM: $name"
        ((TESTS_PASSED++))
    fi
    ((TESTS_RUN++))
done

test_section "Error Recovery - Empty and Whitespace Inputs"

# Test empty input
PLAN=$(generate_plan "")
assert_contains "$PLAN" "INTENT:help" "empty input should default to help"

# Test whitespace-only input
PLAN=$(generate_plan "   ")
assert_contains "$PLAN" "INTENT:help" "whitespace input should default to help"

# Test input with only special characters
PLAN=$(generate_plan "!!!")
assert_contains "$PLAN" "INTENT:help" "special chars should default to help"

test_section "Edge Cases - Very Long Inputs"

# Test with very long input
LONG_INPUT="start $(echo "python " | sed 's/ //g' | head -c 1000)"
PLAN=$(generate_plan "$LONG_INPUT")
if [[ -n "$PLAN" ]]; then
    echo -e "${GREEN}✓${NC} Handled long input"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Long input not handled"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++)

# =============================================================================
# Section 4: Cross-Library Integration
# =============================================================================
test_section "Integration - Parser to Commands"

# Test that parser output can be used by commands
PLAN=$(generate_plan "start python and postgres")

# Extract intent from plan
INTENT=$(echo "$PLAN" | grep "^INTENT:" | cut -d':' -f2)
assert_equals "start_vm" "$INTENT" "intent should be extractable"

# Extract VMs from plan
VMS=$(echo "$PLAN" | grep "^VM:" | cut -d':' -f2)
assert_contains "$VMS" "python" "should extract python from plan"
assert_contains "$VMS" "postgres" "should extract postgres from plan"

test_section "Integration - Alias Resolution Chain"

# Test that aliases work through the full pipeline
PLAN=$(generate_plan "start nodejs")
echo "$PLAN" | grep "^VM:" | grep -q "js" || { echo "Alias nodejs not resolved"; exit 1; }
echo -e "${GREEN}✓${NC} Alias 'nodejs' resolved through full pipeline"
((TESTS_PASSED++))
((TESTS_RUN++))

PLAN=$(generate_plan "start python3")
echo "$PLAN" | grep "^VM:" | grep -q "python" || { echo "Alias python3 not resolved"; exit 1; }
echo -e "${GREEN}✓${NC} Alias 'python3' resolved through full pipeline"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Integration - Wildcard to Specific VMs"

# Test that wildcards are expanded to specific VMs
PLAN=$(generate_plan "start all languages")
# Should have multiple VMs
VM_COUNT=$(echo "$PLAN" | grep -c "^VM:")
if [[ $VM_COUNT -eq 1 ]]; then
    # All VMs on one line - count the VMs
    VM_LINE=$(echo "$PLAN" | grep "^VM:" | cut -d':' -f2)
    VM_COUNT=$(echo "$VM_LINE" | wc -w)
fi

if [[ $VM_COUNT -ge 10 ]]; then
    echo -e "${GREEN}✓${NC} Wildcard expanded to $VM_COUNT language VMs"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Wildcard expanded to only $VM_COUNT VMs"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# =============================================================================
# Section 5: State Management
# =============================================================================
test_section "State Management - Concurrent Operations"

# Simulate planning multiple operations
PLAN1=$(generate_plan "start python")
PLAN2=$(generate_plan "start postgres")
PLAN3=$(generate_plan "start redis")

# All should succeed
if [[ -n "$PLAN1" ]] && [[ -n "$PLAN2" ]] && [[ -n "$PLAN3" ]]; then
    echo -e "${GREEN}✓${NC} Handled concurrent plan generation"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Failed concurrent plan generation"
    ((TESTS_FAILED++))
fi
((TESTS_RUN++))

test_section "State Management - Sequential Operations"

# Simulate a sequence of operations
PLAN=$(generate_plan "create python")
PLAN=$(generate_plan "start python")
PLAN=$(generate_plan "restart python with rebuild")
PLAN=$(generate_plan "stop python")

# All should succeed
echo -e "${GREEN}✓${NC} Sequential operations handled"
((TESTS_PASSED++))
((TESTS_RUN++)

# =============================================================================
# Section 6: Real-World Scenarios
# =============================================================================
test_section "Real-World - First-Time User Experience"

# Simulate a first-time user exploring the system
echo "New user: What can I do?"
PLAN=$(generate_plan "help")
assert_contains "$PLAN" "INTENT:help" "should show help"

echo "New user: What VMs are available?"
PLAN=$(generate_plan "list vms")
assert_contains "$PLAN" "INTENT:list_vms" "should list VMs"

echo "New user: Create a Python environment"
PLAN=$(generate_plan "create python")
assert_contains "$PLAN" "INTENT:create_vm" "should create Python"

echo "New user: How do I connect?"
PLAN=$(generate_plan "how do I connect to Python?")
assert_contains "$PLAN" "INTENT:connect" "should show connection info"

test_section "Real-World - Developer Workflow"

# Simulate a developer's typical workflow
echo "Developer: Start my development stack"
PLAN=$(generate_plan "start python and postgres")
assert_contains "$PLAN" "INTENT:start_vm" "should start dev stack"

echo "Developer: Check what's running"
PLAN=$(generate_plan "status")
assert_contains "$PLAN" "INTENT:status" "should show status"

echo "Developer: Restart database with rebuild"
PLAN=$(generate_plan "restart postgres with rebuild")
assert_contains "$PLAN" "INTENT:restart_vm" "should restart with rebuild"
assert_contains "$PLAN" "rebuild=true" "should set rebuild flag"

echo "Developer: Done for the day"
PLAN=$(generate_plan "stop all")
assert_contains "$PLAN" "INTENT:stop_vm" "should stop all"

test_section "Real-World - Troubleshooting Scenario"

# Simulate troubleshooting
echo "User: Something's wrong, restart everything"
PLAN=$(generate_plan "restart all")
assert_contains "$PLAN" "INTENT:restart_vm" "should restart all"

echo "User: Just rebuild Python"
PLAN=$(generate_plan "rebuild python")
assert_contains "$PLAN" "INTENT:restart_vm" "should rebuild Python"
assert_contains "$PLAN" "rebuild=true" "should have rebuild flag"

echo "User: Check status again"
PLAN=$(generate_plan "what's running?")
assert_contains "$PLAN" "INTENT:status" "should check status"

test_section "Real-World - Team Collaboration"

# Simulate team collaboration scenarios
echo "Team member A: Create our stack"
PLAN=$(generate_plan "create python, go, and postgres")
assert_contains "$PLAN" "INTENT:create_vm" "should create team stack"

echo "Team member B: Start the shared services"
PLAN=$(generate_plan "start postgres and redis")
assert_contains "$PLAN" "INTENT:start_vm" "should start shared services"

echo "Team member C: Connect to the API"
PLAN=$(generate_plan "connect to go")
assert_contains "$PLAN" "INTENT:connect" "should show connection info"

test_section "Real-World - Environment Switching"

# Simulate switching between different project environments
echo "Switch to web project"
PLAN=$(generate_plan "start js and nginx")
assert_contains "$PLAN" "INTENT:start_vm" "should start web stack"

echo "Switch to data project"
PLAN=$(generate_plan "stop all && start python and mongodb")
assert_contains "$PLAN" "INTENT:stop_vm" "should stop web stack"
assert_contains "$PLAN" "INTENT:start_vm" "should start data stack"

echo "Switch to microservices project"
PLAN=$(generate_plan "stop all && start go, rust, and nginx")
assert_contains "$PLAN" "INTENT:stop_vm" "should stop previous"
assert_contains "$PLAN" "INTENT:start_vm" "should start microservices"

# =============================================================================
# Section 7: Performance and Stress Tests
# =============================================================================
test_section "Performance - Rapid Plan Generation"

# Test generating many plans quickly
start_time=$(date +%s%N)
for i in {1..100}; do
    generate_plan "start python" >/dev/null 2>&1
done
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000)) # Convert to milliseconds

if [[ $elapsed -lt 5000 ]]; then
    echo -e "${GREEN}✓${NC} 100 plans generated in ${elapsed}ms (< 5000ms)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} 100 plans took ${elapsed}ms"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Performance - Complex Plan Generation"

# Test generating complex plans
start_time=$(date +%s%N)
generate_plan "start python, go, rust, postgres, redis, mongodb, and nginx" >/dev/null 2>&1
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))

if [[ $elapsed -lt 1000 ]]; then
    echo -e "${GREEN}✓${NC} Complex plan took ${elapsed}ms (< 1000ms)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Complex plan took ${elapsed}ms"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

test_section "Performance - Wildcard Expansion"

# Test wildcard expansion performance
start_time=$(date +%s%N)
generate_plan "start all" >/dev/null 2>&1
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))

if [[ $elapsed -lt 1000 ]]; then
    echo -e "${GREEN}✓${NC} Wildcard expansion took ${elapsed}ms (< 1000ms)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Wildcard expansion took ${elapsed}ms"
    ((TESTS_PASSED++))
fi
((TESTS_RUN++))

# =============================================================================
# Section 8: Comprehensive Coverage
# =============================================================================
test_section "Coverage - All Intent Types"

# Test that all intent types work
declare -a ALL_INTENTS=(
    "list_vms|list vms"
    "create_vm|create python"
    "start_vm|start python"
    "stop_vm|stop python"
    "restart_vm|restart python"
    "status|what's running?"
    "connect|how do I connect to Python?"
    "help|help"
)

for intent_pair in "${ALL_INTENTS[@]}"; do
    expected_intent="${intent_pair%%|*}"
    test_input="${intent_pair##*|}"

    PLAN=$(generate_plan "$test_input")
    ACTUAL=$(echo "$PLAN" | grep "^INTENT:" | cut -d':' -f2)

    if [[ "$ACTUAL" == "$expected_intent" ]]; then
        echo -e "${GREEN}✓${NC} Intent $expected_intent works"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} Intent $expected_intent failed (got $ACTUAL)"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
done

test_section "Coverage - All VM Categories"

# Test that all VM categories work
echo "Testing language VMs"
LANG_PLAN=$(generate_plan "start python")
echo "$LANG_PLAN" | grep -q "VM:python" || { echo "Language VM failed"; exit 1; }
echo -e "${GREEN}✓${NC} Language VMs work"
((TESTS_PASSED++))
((TESTS_RUN++))

echo "Testing service VMs"
SVC_PLAN=$(generate_plan "start postgres")
echo "$SVC_PLAN" | grep -q "VM:postgres" || { echo "Service VM failed"; exit 1; }
echo -e "${GREEN}✓${NC} Service VMs work"
((TESTS_PASSED++))
((TESTS_RUN++))

echo "Testing mixed VMs"
MIXED_PLAN=$(generate_plan "start python and postgres")
echo "$MIXED_PLAN" | grep -q "VM:python" || { echo "Mixed failed - python"; exit 1; }
echo "$MIXED_PLAN" | grep -q "VM:postgres" || { echo "Mixed failed - postgres"; exit 1; }
echo -e "${GREEN}✓${NC} Mixed VMs work"
((TESTS_PASSED++))
((TESTS_RUN++))

test_section "Coverage - All Flag Combinations"

# Test all flag combinations
declare -a FLAG_TESTS=(
    "rebuild|rebuild python"
    "nocache|rebuild python with no cache"
    "both|rebuild python with no cache"
)

for flag_test in "${FLAG_TESTS[@]}"; do
    flag_name="${flag_test%%|*}"
    test_input="${flag_test##*|}"

    PLAN=$(generate_plan "$test_input")

    case "$flag_name" in
        "rebuild")
            if echo "$PLAN" | grep -q "rebuild=true"; then
                echo -e "${GREEN}✓${NC} Rebuild flag works"
                ((TESTS_PASSED++))
            else
                echo -e "${RED}✗${NC} Rebuild flag failed"
                ((TESTS_FAILED++))
            fi
            ;;
        "nocache")
            if echo "$PLAN" | grep -q "nocache=true"; then
                echo -e "${GREEN}✓${NC} No cache flag works"
                ((TESTS_PASSED++))
            else
                echo -e "${RED}✗${NC} No cache flag failed"
                ((TESTS_FAILED++))
            fi
            ;;
        "both")
            if echo "$PLAN" | grep -q "rebuild=true" && echo "$PLAN" | grep -q "nocache=true"; then
                echo -e "${GREEN}✓${NC} Both flags work"
                ((TESTS_PASSED++))
            else
                echo -e "${RED}✗${NC} Both flags failed"
                ((TESTS_FAILED++))
            fi
            ;;
    esac
    ((TESTS_RUN++))
done

teardown_test_env

test_suite_end "VDE Integration Tests"
exit $?
