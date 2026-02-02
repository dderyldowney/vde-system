#!/usr/bin/env zsh
# Unit Tests for vde-parser Library
# Tests natural language parser functionality

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vm-common"
source "$PROJECT_ROOT/scripts/lib/vde-commands"
source "$PROJECT_ROOT/scripts/lib/vde-parser"

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

# Initialize VM types for parser tests
load_vm_types --no-cache >/dev/null 2>&1

# =============================================================================
# TESTS: Intent Detection
# =============================================================================

test_detect_list_intent() {
    test_start "detect list intent"

    local inputs=(
        "list all vms"
        "show all languages"
        "what vms can I create"
        "show services"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "list_vms" ]]; then
            test_fail "detect list intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect list intent"
}

test_detect_create_intent() {
    test_start "detect create intent"

    local inputs=(
        "create a go vm"
        "create new rust"
        "make a python"
        "set up js"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "create_vm" ]]; then
            test_fail "detect create intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect create intent"
}

test_detect_start_intent() {
    test_start "detect start intent"

    local inputs=(
        "start python"
        "launch the rust vm"
        "boot go"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "start_vm" ]]; then
            test_fail "detect start intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect start intent"
}

test_detect_stop_intent() {
    test_start "detect stop intent"

    local inputs=(
        "stop python"
        "shutdown rust"
        "kill the go vm"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "stop_vm" ]]; then
            test_fail "detect stop intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect stop intent"
}

test_detect_restart_intent() {
    test_start "detect restart intent"

    local inputs=(
        "restart python"
        "reboot rust"
        "rebuild go"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "restart_vm" ]]; then
            test_fail "detect restart intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect restart intent"
}

test_detect_status_intent() {
    test_start "detect status intent"

    local inputs=(
        "what's running"
        "check status"
        "current state"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "status" ]]; then
            test_fail "detect status intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect status intent"
}

test_detect_connect_intent() {
    test_start "detect connect intent"

    local inputs=(
        "how do I connect to python"
        "ssh into rust"
        "connect to go"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "connect" ]]; then
            test_fail "detect connect intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect connect intent"
}

test_detect_help_intent() {
    test_start "detect help intent"

    local inputs=(
        "help"
        "what can I do"
        "how do I use vde"
    )

    for input in "${inputs[@]}"; do
        local intent
        intent=$(detect_intent "$input")
        if [[ "$intent" != "help" ]]; then
            test_fail "detect help intent" "input '$input' gave intent '$intent'"
            return
        fi
    done

    test_pass "detect help intent"
}

# =============================================================================
# TESTS: Entity Extraction
# =============================================================================

test_extract_vm_names() {
    test_start "extract vm names"

    local result
    result=$(extract_vm_names "start python and rust")

    if echo "$result" | grep -q "python" && echo "$result" | grep -q "rust"; then
        test_pass "extract vm names"
        return
    fi

    test_fail "extract vm names" "names not found in: $result"
}

test_extract_vm_names_all() {
    test_start "extract vm names (all)"

    local result
    result=$(extract_vm_names "start everything")

    # Should get all VMs
    local count
    count=$(echo "$result" | wc -w)
    if [[ $count -gt 5 ]]; then
        test_pass "extract vm names (all)"
        return
    fi

    test_fail "extract vm names" "expected multiple VMs, got $count"
}

test_extract_vm_aliases() {
    test_start "extract vm aliases"

    local result
    result=$(extract_vm_names "start python3")

    if echo "$result" | grep -q "python"; then
        test_pass "extract vm aliases"
        return
    fi

    test_fail "extract vm aliases" "alias 'python3' not resolved to 'python': $result"
}

test_extract_filter() {
    test_start "extract filter"

    if [[ "$(extract_filter "show all languages")" == "lang" ]]; then
        if [[ "$(extract_filter "list services")" == "svc" ]]; then
            test_pass "extract filter"
            return
        fi
    fi

    test_fail "extract filter" "filter extraction failed"
}

test_extract_flags_rebuild() {
    test_start "extract flags (rebuild)"

    local result
    result=$(extract_flags "rebuild python with no cache")

    if echo "$result" | grep -q "rebuild=true"; then
        test_pass "extract flags (rebuild)"
        return
    fi

    test_fail "extract flags" "rebuild flag not found in: $result"
}

test_extract_flags_nocache() {
    test_start "extract flags (no-cache)"

    local result
    result=$(extract_flags "rebuild with no cache")

    if echo "$result" | grep -q "nocache=true"; then
        test_pass "extract flags (no-cache)"
        return
    fi

    test_fail "extract flags" "nocache flag not found in: $result"
}

# =============================================================================
# TESTS: Plan Generation
# =============================================================================

test_generate_plan_list() {
    test_start "generate plan (list)"

    local plan
    plan=$(generate_plan "list all vms")

    if echo "$plan" | grep -q "INTENT:list_vms"; then
        test_pass "generate plan (list)"
        return
    fi

    test_fail "generate plan" "intent not found in plan"
}

test_generate_plan_create() {
    test_start "generate plan (create)"

    local plan
    plan=$(generate_plan "create a go vm")

    if echo "$plan" | grep -q "INTENT:create_vm"; then
        if echo "$plan" | grep -q "VM:go"; then
            test_pass "generate plan (create)"
            return
        fi
    fi

    test_fail "generate plan" "intent or VM not found in plan"
}

test_generate_plan_with_flags() {
    test_start "generate plan (with flags)"

    local plan
    plan=$(generate_plan "rebuild python with no cache")

    if echo "$plan" | grep -q "INTENT:restart_vm"; then
        if echo "$plan" | grep -q "FLAGS:.*rebuild=true"; then
            if echo "$plan" | grep -q "nocache=true"; then
                test_pass "generate plan (with flags)"
                return
            fi
        fi
    fi

    test_fail "generate plan" "flags not found in plan"
}

# =============================================================================
# TESTS: Security Validation
# =============================================================================

test_validate_plan_line_valid() {
    test_start "validate plan line (valid)"

    local valid_lines=(
        "INTENT:start_vm"
        "VM:python"
        "FLAGS:rebuild=true nocache=false"
        "FILTER:all"
    )

    for line in "${valid_lines[@]}"; do
        if ! validate_plan_line "$line"; then
            test_fail "validate plan line" "valid line rejected: $line"
            return
        fi
    done

    test_pass "validate plan line (valid)"
}

test_validate_plan_line_invalid_key() {
    test_start "validate plan line (invalid key)"

    if validate_plan_line "MALICIOUS:command"; then
        test_fail "validate plan line" "invalid key should be rejected"
        return
    fi

    test_pass "validate plan line (invalid key)"
}

test_validate_plan_line_dangerous_chars() {
    test_start "validate plan line (dangerous chars)"

    local dangerous_lines=(
        "VM:python; rm -rf /"
        "VM:python|cat /etc/passwd"
        "VM:python\$(whoami)"
    )

    for line in "${dangerous_lines[@]}"; do
        if validate_plan_line "$line"; then
            test_fail "validate plan line" "dangerous line accepted: $line"
            return
        fi
    done

    test_pass "validate plan line (dangerous chars)"
}

test_contains_dangerous_chars() {
    test_start "contains_dangerous_chars"

    local dangerous=';|&`$(){}[]<>!#*?\'
    # Test a few dangerous characters
    if contains_dangerous_chars "test;rm -rf"; then
        if contains_dangerous_chars "test|pipe"; then
            if contains_dangerous_chars "test\$(cmd)"; then
                test_pass "contains_dangerous_chars"
                return
            fi
        fi
    fi

    test_fail "contains_dangerous_chars" "dangerous chars not detected"
}

test_parse_flags() {
    test_start "parse_flags"

    local flags="rebuild=true nocache=false"
    if parse_flags "$flags"; then
        if [[ "$rebuild" == "true" ]] && [[ "$nocache" == "false" ]]; then
            test_pass "parse_flags"
            return
        fi
    fi

    test_fail "parse_flags" "flags not parsed correctly"
}

test_parse_flags_invalid() {
    test_start "parse_flags (invalid)"

    # Invalid flag value
    if parse_flags "rebuild=yes"; then
        test_fail "parse_flags" "invalid value should be rejected"
        return
    fi

    test_pass "parse_flags (invalid)"
}

# =============================================================================
# TESTS: Alias Map
# =============================================================================

test_build_alias_map() {
    test_start "build_alias_map"

    _build_alias_map

    # Check that map is marked as built
    if [[ $_VM_ALIAS_MAP_BUILT -eq 1 ]]; then
        test_pass "build_alias_map"
        return
    fi

    test_fail "build_alias_map" "map not marked as built"
}

test_lookup_vm_by_alias() {
    test_start "lookup_vm_by_alias"

    _build_alias_map

    local result
    result=$(_lookup_vm_by_alias "python3")

    if [[ "$result" == "python" ]]; then
        test_pass "lookup_vm_by_alias"
        return
    fi

    test_fail "lookup_vm_by_alias" "alias not resolved: $result"
}

test_invalidate_alias_map() {
    test_start "invalidate_alias_map"

    _build_alias_map
    invalidate_alias_map

    if [[ $_VM_ALIAS_MAP_BUILT -eq 0 ]]; then
        test_pass "invalidate_alias_map"
        return
    fi

    test_fail "invalidate_alias_map" "map not invalidated"
}

# =============================================================================
# TESTS: Source Guard
# =============================================================================

test_parser_source_guard() {
    test_start "parser source guard"

    # Should be loaded after first source
    if [[ "${_VDE_PARSER_LOADED:-}" == "1" ]]; then
        test_pass "parser source guard"
        return
    fi

    test_fail "parser source guard" "source guard not set"
}

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "Unit Tests: vde-parser"
    echo "=========================================="
    echo ""

    # Intent Detection
    test_detect_list_intent
    test_detect_create_intent
    test_detect_start_intent
    test_detect_stop_intent
    test_detect_restart_intent
    test_detect_status_intent
    test_detect_connect_intent
    test_detect_help_intent

    # Entity Extraction
    test_extract_vm_names
    test_extract_vm_names_all
    test_extract_vm_aliases
    test_extract_filter
    test_extract_flags_rebuild
    test_extract_flags_nocache

    # Plan Generation
    test_generate_plan_list
    test_generate_plan_create
    test_generate_plan_with_flags

    # Security Validation
    test_validate_plan_line_valid
    test_validate_plan_line_invalid_key
    test_validate_plan_line_dangerous_chars
    test_contains_dangerous_chars
    test_parse_flags
    test_parse_flags_invalid

    # Alias Map
    test_build_alias_map
    test_lookup_vm_by_alias
    test_invalidate_alias_map

    # Source Guard
    test_parser_source_guard

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
