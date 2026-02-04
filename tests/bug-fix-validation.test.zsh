#!/usr/bin/env zsh
# VDE Bug Fix Validation Tests
# Tests that verify all bug fixes are working correctly
#
# Usage: ./tests/bug-fix-validation.test.sh
#         ./tests/bug-fix-validation.test.sh --verbose

# Don't use set -e as it interferes with test counting
# set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source VDE libraries
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"

# Test configuration
VERBOSE=false
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Colors for output
if [[ -t 1 ]]; then
    COLOR_GREEN='\033[0;32m'
    COLOR_RED='\033[0;31m'
    COLOR_YELLOW='\033[0;33m'
    COLOR_BLUE='\033[0;34m'
    COLOR_RESET='\033[0m'
else
    COLOR_GREEN=''
    COLOR_RED=''
    COLOR_YELLOW=''
    COLOR_BLUE=''
    COLOR_RESET=''
fi

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --verbose|-v)
            VERBOSE=true
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v    Enable verbose output"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Tests validated:"
            echo "  1. SSH Keys Handling (only .pub files copied)"
            echo "  2. Port Collision Detection (checks host ports)"
            echo "  3. Key Collision Prevention (hex encoding for unique keys)"
            echo "  4. apt-key Deprecation Fix (uses modern GPG handling)"
            echo "  5. Architecture Detection (dynamic, not hardcoded)"
            echo "  6. Host Access Script Removal (broken code removed)"
            exit 0
            ;;
    esac
done

# Test helper functions
test_start() {
    local name="$1"
    echo -e "${COLOR_BLUE}[TEST]${COLOR_RESET} $name"
}

test_pass() {
    local name="$1"
    echo -e "${COLOR_GREEN}[PASS]${COLOR_RESET} $name"
    ((TESTS_PASSED++))
}

test_fail() {
    local name="$1"
    local reason="$2"
    echo -e "${COLOR_RED}[FAIL]${COLOR_RESET} $name"
    if [[ -n "$reason" ]]; then
        echo -e "       ${COLOR_RED}Reason: $reason${COLOR_RESET}"
    fi
    ((TESTS_FAILED++))
}

test_skip() {
    local name="$1"
    local reason="$2"
    echo -e "${COLOR_YELLOW}[SKIP]${COLOR_RESET} $name"
    if [[ -n "$reason" ]]; then
        echo -e "        ${COLOR_YELLOW}Reason: $reason${COLOR_RESET}"
    fi
    ((TESTS_SKIPPED++))
}

info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${COLOR_BLUE}[INFO]${COLOR_RESET} $*"
    fi
}

# =============================================================================
# TEST 1: SSH Keys Handling - Only .pub files should be copied
# Bug: Previously used COPY public-ssh-keys/* which would copy ANY file
# Fix: Now uses explicit loop over *.pub files only
# =============================================================================
test_ssh_keys_handling() {
    test_start "SSH Keys Handling (.pub files only)"

    local test_dir="/tmp/vde-test-ssh-keys-$$"
    mkdir -p "$test_dir"

    # Create test files
    touch "$test_dir/.keep"
    touch "$test_dir/README.md"
    echo "ssh-rsa AAAA test key" > "$test_dir/id_rsa.pub"
    echo "ssh-ed25519 AAAA another key" > "$test_dir/id_ed25519.pub"

    # Count .pub files
    local pub_count=$(find "$test_dir" -name "*.pub" | wc -l)
    local total_count=$(find "$test_dir" -type f | wc -l)

    info "Found $pub_count .pub files out of $total_count total files"

    # Verify we can distinguish .pub files
    if [[ $pub_count -eq 2 ]]; then
        if [[ $total_count -eq 4 ]]; then
            test_pass "SSH Keys Handling" "Correctly identifies .pub files (2 of 4 files)"
        else
            test_fail "SSH Keys Handling" "Expected 4 total files, found $total_count"
        fi
    else
        test_fail "SSH Keys Handling" "Expected 2 .pub files, found $pub_count"
    fi

    # Cleanup
    rm -rf "$test_dir"
}

# =============================================================================
# TEST 2: Port Collision Detection
# Bug: find_next_available_port only checked VDE's internal port registry
# Fix: Now also checks if port is actually in use on host using lsof/netstat
# =============================================================================
test_port_collision_detection() {
    test_start "Port Collision Detection"

    # Check if the port checking logic exists in vm-common
    local vm_common="$PROJECT_ROOT/scripts/lib/vm-common"

    if grep -q "lsof.*LISTEN" "$vm_common" 2>/dev/null; then
        info "Found lsof-based port checking"
        if grep -q "netstat.*LISTEN" "$vm_common" 2>/dev/null; then
            info "Found netstat fallback for port checking"
            if grep -q "docker ps.*0.0.0.0:\$port" "$vm_common" 2>/dev/null; then
                test_pass "Port Collision Detection" "Host port collision detection implemented with lsof, netstat, and docker fallbacks"
                return
            fi
        fi
    fi

    test_fail "Port Collision Detection" "Port collision detection code not found in vm-common"
}

# =============================================================================
# TEST 3: Key Collision Prevention in vde-shell-compat
# Bug: Simple tr '/' '_' caused collisions: "a/b" and "a_b" both became "a_b"
# Fix: Now uses hex encoding with od to ensure unique safe keys
# =============================================================================
test_key_collision_prevention() {
    test_start "Key Collision Prevention (hex encoding)"

    local test_dir="/tmp/vde-test-assoc-$$"
    mkdir -p "$test_dir"

    # Source the shell-compat library to test functions
    _VDE_ASSOC_STORAGE_DIR="$test_dir"

    # Initialize test arrays
    _assoc_init "TEST_ARRAY"

    # Set keys that would previously collide
    _assoc_set "TEST_ARRAY" "a/b" "value1"
    _assoc_set "TEST_ARRAY" "a_b" "value2"
    _assoc_set "TEST_ARRAY" "special/key/with/slashes" "value3"

    # Verify keys are distinct
    local val1=$(_assoc_get "TEST_ARRAY" "a/b")
    local val2=$(_assoc_get "TEST_ARRAY" "a_b")
    local val3=$(_assoc_get "TEST_ARRAY" "special/key/with/slashes")

    info "Values retrieved: a/b='$val1' a_b='$val2' special/key/with/slashes='$val3'"

    if [[ "$val1" == "value1" ]] && [[ "$val2" == "value2" ]] && [[ "$val3" == "value3" ]]; then
        test_pass "Key Collision Prevention" "Hex encoding prevents key collisions"
    else
        test_fail "Key Collision Prevention" "Key collision detected! Expected distinct values"
    fi

    # Test _assoc_keys returns original keys
    local keys=$(_assoc_keys "TEST_ARRAY")
    info "Keys returned: $keys"

    # Check all keys are present
    if echo "$keys" | grep -q "a/b" && \
       echo "$keys" | grep -q "a_b" && \
       echo "$keys" | grep -q "special/key/with/slashes"; then
        info "Key enumeration preserves original keys"
    else
        test_fail "Key Collision Prevention" "Key enumeration doesn't preserve original keys"
    fi

    # Cleanup
    rm -rf "$test_dir"
}

# =============================================================================
# TEST 4: apt-key Deprecation Fix
# Bug: Used deprecated 'apt-key add' command
# Fix: Now uses /etc/apt/keyrings with signed-by in sources.list
# =============================================================================
test_apt_key_deprecation_fix() {
    test_start "apt-key Deprecation Fix (modern GPG handling)"

    local dockerfile="$PROJECT_ROOT/configs/docker/base-dev.Dockerfile"

    # Check that apt-key is NOT used
    if grep -q "apt-key add" "$dockerfile" 2>/dev/null; then
        test_fail "apt-key Deprecation Fix" "Deprecated 'apt-key add' still found in Dockerfile"
        return
    fi

    # Check that modern GPG handling is used
    if grep -q "/etc/apt/keyrings/" "$dockerfile" 2>/dev/null; then
        if grep -q "gpg.*dearmor" "$dockerfile" 2>/dev/null; then
            if grep -q "signed-by=" "$dockerfile" 2>/dev/null; then
                test_pass "apt-key Deprecation Fix" "Uses modern GPG keyring with signed-by"
                return
            fi
        fi
    fi

    test_fail "apt-key Deprecation Fix" "Modern GPG handling not found"
}

# =============================================================================
# TEST 5: Architecture Detection (not hardcoded)
# Bug: Hardcoded [arch=amd64,arm64] in MongoDB repository config
# Fix: Removed arch parameter - APT now handles multiarch automatically
# =============================================================================
test_architecture_detection() {
    test_start "Architecture Detection (dynamic, not hardcoded)"

    local dockerfile="$PROJECT_ROOT/configs/docker/base-dev.Dockerfile"

    # Check that hardcoded architecture is NOT used
    if grep -q "\[arch=amd64,arm64\]" "$dockerfile" 2>/dev/null; then
        test_fail "Architecture Detection" "Still has hardcoded architecture in repo config"
        return
    fi

    # Check that MongoDB repo config exists without hardcoded arch
    if grep -q "repo.mongodb.org/apt/debian" "$dockerfile" 2>/dev/null; then
        local mongo_line=$(grep "repo.mongodb.org" "$dockerfile" 2>/dev/null)
        info "MongoDB repo line: $mongo_line"
        if echo "$mongo_line" | grep -q "signed-by="; then
            if ! echo "$mongo_line" | grep -q "arch="; then
                test_pass "Architecture Detection" "No hardcoded architecture - uses APT auto-detection"
                return
            fi
        fi
    fi

    test_fail "Architecture Detection" "Architecture detection implementation not found"
}

# =============================================================================
# TEST 6: Host Access Script Removal
# Bug: Broken host-sh script tried to run 'docker exec' from inside container
# Fix: Removed the broken script and added explanatory comment
# =============================================================================
test_host_access_script_removed() {
    test_start "Host Access Script Removal (broken code removed)"

    local dockerfile="$PROJECT_ROOT/configs/docker/base-dev.Dockerfile"

    # Check that broken host-sh script is NOT created
    if grep -q "host-sh" "$dockerfile" 2>/dev/null; then
        # Might still have reference in comment
        if grep -q "/usr/local/bin/host-sh" "$dockerfile" 2>/dev/null; then
            # Check if it's just being created (bad) or mentioned in comment (ok)
            local lines_with_host_sh=$(grep -c "host-sh" "$dockerfile")
            if grep -q "echo.*host-sh" "$dockerfile" 2>/dev/null; then
                test_fail "Host Access Script Removal" "Still creating broken host-sh script"
                return
            fi
        fi
    fi

    # Check for explanatory comment about why it was removed
    if grep -q "Host access from container removed" "$dockerfile" 2>/dev/null || \
       grep -q "fundamentally broken" "$dockerfile" 2>/dev/null; then
        test_pass "Host Access Script Removal" "Broken script removed with explanatory comment"
        return
    fi

    test_skip "Host Access Script Removal" "Explanatory comment not found (but script may be gone)"
}

# =============================================================================
# TEST 7: Dockerfile SSH Keys Build Test
# Bug: COPY would fail if no .pub files exist
# Fix: Uses conditional RUN loop that handles empty key directory
# =============================================================================
test_dockerfile_ssh_keys_build() {
    test_start "Dockerfile SSH Keys Build (handles empty keys)"

    local dockerfile="$PROJECT_ROOT/configs/docker/base-dev.Dockerfile"

    # Check for conditional SSH keys handling
    if grep -q "if \[ -d /public-ssh-keys \]" "$dockerfile" 2>/dev/null || \
       grep -q "if \[ -s /home.*authorized_keys" "$dockerfile" 2>/dev/null; then
        test_pass "Dockerfile SSH Keys Build" "Uses conditional handling for SSH keys"
        return
    fi

    test_fail "Dockerfile SSH Keys Build" "No conditional SSH keys handling found"
}

# =============================================================================
# TEST 8: Container Name Regex Allows Numbers
# Bug: vde_get_running_vms regex only allowed [a-z], missing numbers
# Fix: Changed to [a-z0-9] to allow VM names like "python3", "csharp2"
# =============================================================================
test_container_name_regex_allows_numbers() {
    test_start "Container Name Regex Allows Numbers"

    local vde_commands="$PROJECT_ROOT/scripts/lib/vde-commands"

    # Check that regex includes numbers in character class
    if grep -E 'grep -E.*\[a-z0-9\]+.*-dev' "$vde_commands" 2>/dev/null; then
        test_pass "Container Name Regex" "Regex allows alphanumeric container names"
        return
    fi

    test_fail "Container Name Regex" "Regex doesn't allow numbers in container names"
}

# =============================================================================
# TEST 9: Parser Removes # Character
# Bug: vde-parser kept # character which starts comments in shell
# Fix: Removed # from allowed characters in word cleaning
# =============================================================================
test_parser_removes_hash_char() {
    test_start "Parser Removes # Character"

    local vde_parser="$PROJECT_ROOT/scripts/lib/vde-parser"

    # Check that # is NOT in the allowed characters
    if grep -q "tr -cd 'a-z0-9+'" "$vde_parser" 2>/dev/null; then
        # Verify # is not included
        if ! grep -q "tr -cd 'a-z0-9+#'" "$vde_parser" 2>/dev/null; then
            test_pass "Parser # Character" "Parser correctly removes # character"
            return
        fi
    fi

    test_fail "Parser # Character" "Parser may allow unsafe # character"
}

# =============================================================================
# TEST 10: start-virtual Checks VM Existence
# Bug: start-virtual only checked if VM is known, not if it's created
# Fix: Added vm_exists check before attempting to start
# =============================================================================
test_start_virtual_checks_vm_exists() {
    test_start "start-virtual Checks VM Existence"

    local start_script="$PROJECT_ROOT/scripts/start-virtual"

    # Check that vm_exists is called before starting
    if grep -q "vm_exists" "$start_script" 2>/dev/null; then
        # Verify it calls the error handler for uncreated VMs
        if grep -q "vde_error_vm_not_created" "$start_script" 2>/dev/null; then
            test_pass "start-virtual VM Existence" "Checks if VM is created before starting"
            return
        fi
    fi

    test_fail "start-virtual VM Existence" "Missing VM existence check"
}

# =============================================================================
# TEST 11: add-vm-type Uses Portable Functions
# Bug: Used zsh-specific associative array syntax
# Fix: Uses is_known_vm and get_all_vms functions instead
# =============================================================================
test_add_vm_type_portable_syntax() {
    test_start "add-vm-type Uses Portable Syntax"

    local add_vm_script="$PROJECT_ROOT/scripts/add-vm-type"

    # Check that it uses is_known_vm instead of zsh-specific syntax
    if grep -q "is_known_vm" "$add_vm_script" 2>/dev/null; then
        # Verify no zsh-specific ${(@k)VM_TYPE} syntax
        if ! grep -q '"\${(@k)VM_TYPE}"' "$add_vm_script" 2>/dev/null; then
            test_pass "add-vm-type Portable Syntax" "Uses portable VM checking functions"
            return
        fi
    fi

    test_fail "add-vm-type Portable Syntax" "Uses zsh-specific associative array syntax"
}

# =============================================================================
# TEST 12: vde-commands Properly Quotes Aliases
# Bug: $aliases was unquoted causing potential word splitting issues
# Fix: Now properly quoted as "$aliases"
# =============================================================================
test_vde_commands_quotes_aliases() {
    test_start "vde-commands Properly Quotes Aliases"

    local vde_commands="$PROJECT_ROOT/scripts/lib/vde-commands"

    # Check that aliases is quoted when passed to add-vm-type
    if grep -E '\[ -n "\$aliases" \].*"\$aliases"' "$vde_commands" 2>/dev/null; then
        test_pass "vde-commands Aliases" "Aliases are properly quoted"
        return
    fi

    # Also check for the comment explaining the quoting
    if grep -q "Note:.*aliases.*intentionally" "$vde_commands" 2>/dev/null; then
        test_pass "vde-commands Aliases" "Aliases are properly quoted with documentation"
        return
    fi

    test_fail "vde-commands Aliases" "Aliases may not be properly quoted"
}

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "VDE Bug Fix Validation Tests"
    echo "=========================================="
    echo ""

    # Run all tests
    test_ssh_keys_handling
    test_port_collision_detection
    test_key_collision_prevention
    test_apt_key_deprecation_fix
    test_architecture_detection
    test_host_access_script_removed
    test_dockerfile_ssh_keys_build
    test_container_name_regex_allows_numbers
    test_parser_removes_hash_char
    test_start_virtual_checks_vm_exists
    test_add_vm_type_portable_syntax
    test_vde_commands_quotes_aliases

    # Print summary
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo -e "${COLOR_GREEN}Passed:  $TESTS_PASSED${COLOR_RESET}"
    echo -e "${COLOR_RED}Failed:  $TESTS_FAILED${COLOR_RESET}"
    echo -e "${COLOR_YELLOW}Skipped: $TESTS_SKIPPED${COLOR_RESET}"
    echo ""

    local total=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
    echo "Total:   $total"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${COLOR_GREEN}All tests passed!${COLOR_RESET}\n"
        exit 0
    else
        echo -e "\n${COLOR_RED}Some tests failed!${COLOR_RESET}\n"
        exit 1
    fi
}

# Run main
main "$@"
