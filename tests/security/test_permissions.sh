#!/usr/bin/env zsh
# Security Test: File Permissions

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
VDE_ROOT_DIR="$(cd "$TEST_DIR/../.." && pwd)"

TESTS_PASSED=0
TESTS_FAILED=0
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'
test_start() { echo -e "${YELLOW}Testing: $1${RESET}" }
test_pass() { echo -e "  ${GREEN}✓ PASS: $1${RESET}"; ((TESTS_PASSED++)) }
test_fail() { echo -e "  ${RED}✗ FAIL: $1 - $2${RESET}"; ((TESTS_FAILED++)) }

test_scripts_executable() {
    test_start "VDE scripts are executable"
    local vde_script="$VDE_ROOT_DIR/scripts/vde"
    if [[ -x "$vde_script" ]]; then
        test_pass "VDE main script is executable"
    else
        test_fail "scripts_executable" "VDE script is not executable"
    fi
}

test_no_world_writable_scripts() {
    test_start "No world-writable scripts"
    local world_writable=$(find "$VDE_ROOT_DIR/scripts" -perm -o+w -type f 2>/dev/null)
    if [[ -z "$world_writable" ]]; then
        test_pass "no world-writable scripts"
    else
        test_fail "world_writable" "Found world-writable: $world_writable"
    fi
}

test_no_world_writable_configs() {
    test_start "No world-writable config files"
    local configs_dir="$VDE_ROOT_DIR/configs"
    if [[ -d "$configs_dir" ]]; then
        local world_writable=$(find "$configs_dir" -perm -o+w -type f 2>/dev/null)
        if [[ -z "$world_writable" ]]; then
            test_pass "no world-writable configs"
        else
            test_fail "world_writable_configs" "Found: $world_writable"
        fi
    else
        test_pass "no configs directory (skipped)"
    fi
}

test_lib_files_not_world_writable() {
    test_start "Library files not world-writable"
    local world_writable=$(find "$VDE_ROOT_DIR/scripts/lib" -perm -o+w -type f 2>/dev/null)
    if [[ -z "$world_writable" ]]; then
        test_pass "library files protected"
    else
        test_fail "lib_world_writable" "Found: $world_writable"
    fi
}

test_ssh_dir_permissions() {
    test_start "SSH directory permissions"
    local ssh_dir="$HOME/.ssh"
    if [[ -d "$ssh_dir" ]]; then
        local perms=$(stat -f "%Lp" "$ssh_dir" 2>/dev/null || stat -c "%a" "$ssh_dir" 2>/dev/null)
        if [[ "$perms" == "700" ]] || [[ "$perms" == "755" ]]; then
            test_pass "SSH directory permissions OK ($perms)"
        else
            test_fail "ssh_perms" "SSH dir permissions are $perms (expected 700 or 755)"
        fi
    else
        test_pass "SSH directory permissions (no .ssh dir, skipped)"
    fi
}

main() {
    echo ""
    echo "=========================================="
    echo "Security Tests: File Permissions"
    echo "=========================================="
    echo ""

    test_scripts_executable
    test_no_world_writable_scripts
    test_no_world_writable_configs
    test_lib_files_not_world_writable
    test_ssh_dir_permissions

    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo -e "${GREEN}Passed:  $TESTS_PASSED${RESET}"
    echo -e "${RED}Failed:  $TESTS_FAILED${RESET}"
    echo ""

    [[ $TESTS_FAILED -eq 0 ]] && exit 0 || exit 1
}

main "$@"
