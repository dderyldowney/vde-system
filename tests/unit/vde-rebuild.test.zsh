#!/usr/bin/env zsh
# Unit Tests for vde-rebuild Script
# Tests Docker image rebuild functionality

# Don't use set -e as it interferes with test counting

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

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
# TEST: Script exists and is executable
# =============================================================================

test_script_exists() {
    test_start "Script exists and is executable"
    
    local script="$PROJECT_ROOT/bin/vde-rebuild"
    
    if [[ -f "$script" ]]; then
        if [[ -x "$script" ]]; then
            test_pass "Script exists and is executable"
        else
            test_fail "Script exists but is not executable"
        fi
    else
        test_fail "Script does not exist"
    fi
}

# =============================================================================
# TEST: Script has shebang
# =============================================================================

test_shebang() {
    test_start "Script has correct shebang"
    
    local script="$PROJECT_ROOT/bin/vde-rebuild"
    local first_line=$(head -n 1 "$script")
    
    if [[ "$first_line" =~ ^#!.*zsh$ ]]; then
        test_pass "Script has zsh shebang"
    else
        test_fail "Script shebang is incorrect: $first_line"
    fi
}

# =============================================================================
# TEST: Script has help option
# =============================================================================

test_help_option() {
    test_start "Script has --help option"
    
    local output="$($PROJECT_ROOT/bin/vde-rebuild --help 2>&1)"
    
    if echo "$output" | grep -q "Usage:"; then
        test_pass "Script has --help option"
    else
        test_fail "Script does not have --help option"
    fi
}

# =============================================================================
# TEST: Script has no-cache option
# =============================================================================

test_nocache_option() {
    test_start "Script has --no-cache option"
    
    local output="$($PROJECT_ROOT/bin/vde-rebuild --help 2>&1)"
    
    if echo "$output" | grep -q "\-\-no-cache"; then
        test_pass "Script has --no-cache option"
    else
        test_fail "Script does not have --no-cache option"
    fi
}

# =============================================================================
# TEST: Script has vm option
# =============================================================================

test_vm_option() {
    test_start "Script has --vm option"
    
    local output="$($PROJECT_ROOT/bin/vde-rebuild --help 2>&1)"
    
    if echo "$output" | grep -q "\-\-vm"; then
        test_pass "Script has --vm option"
    else
        test_fail "Script does not have --vm option"
    fi
}

# =============================================================================
# TEST: vde command includes rebuild
# =============================================================================

test_vde_command_includes_rebuild() {
    test_start "vde command includes rebuild"
    
    local output="$($PROJECT_ROOT/bin/vde help 2>&1)"
    
    if echo "$output" | grep -q "rebuild"; then
        test_pass "vde command includes rebuild"
    else
        test_fail "vde command does not include rebuild"
    fi
}

# =============================================================================
# TEST: Docker is available
# =============================================================================

test_docker_available() {
    test_start "Docker is available"
    
    if command -v docker &>/dev/null; then
        if docker info &>/dev/null; then
            test_pass "Docker is available and running"
        else
            test_fail "Docker is installed but not running"
        fi
    else
        test_fail "Docker is not installed"
    fi
}

# =============================================================================
# TEST: vde-base image exists
# =============================================================================

test_vde_base_image_exists() {
    test_start "vde-base:latest image exists"
    
    if docker image inspect vde-base:latest &>/dev/null; then
        test_pass "vde-base:latest exists"
    else
        test_fail "vde-base:latest does not exist"
    fi
}

# =============================================================================
# TEST: All VM images exist
# =============================================================================

test_all_vm_images_exist() {
    test_start "All VM images exist"
    
    # Count existing vde- images (excluding vde-base)
    local count=$(docker images --format '{{.Repository}}' 2>/dev/null | grep '^vde-' | grep -v ':base$' | wc -l | tr -d ' ')
    
    # We expect 26+ VM images
    if [[ $count -ge 26 ]]; then
        test_pass "All VM images exist ($count VMs)"
    else
        test_fail "Only $count VM images found (expected 26+)"
    fi
}

# =============================================================================
# TEST: Rebuild base only
# =============================================================================

test_rebuild_base_only() {
    test_start "Can rebuild base only (--vm base)"
    
    # This should complete without error
    local output="$($PROJECT_ROOT/bin/vde-rebuild --vm base 2>&1)"
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        test_pass "Can rebuild base only"
    else
        test_fail "Failed to rebuild base: $output"
    fi
}

# =============================================================================
# TEST: Rebuild specific VM
# =============================================================================

test_rebuild_specific_vm() {
    test_start "Can rebuild specific VM (--vm python)"
    
    # This should complete without error
    local output="$($PROJECT_ROOT/bin/vde-rebuild --vm python 2>&1)"
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        test_pass "Can rebuild specific VM"
    else
        test_fail "Failed to rebuild specific VM: $output"
    fi
}

# =============================================================================
# MAIN
# =============================================================================

echo ""
echo "Running vde-rebuild Unit Tests"
echo "================================"
echo ""

# Run tests that don't require Docker
test_script_exists
test_shebang
test_help_option
test_nocache_option
test_vm_option
test_vde_command_includes_rebuild

# Run tests that require Docker (if available)
if docker info &>/dev/null 2>&1; then
    test_docker_available
    test_vde_base_image_exists
    test_all_vm_images_exist
    
    # Only run rebuild tests if images exist
    if docker image inspect vde-base:latest &>/dev/null; then
        test_rebuild_base_only
        test_rebuild_specific_vm
    fi
fi

echo ""
echo "================================"
echo "Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
    exit 1
fi

exit 0
