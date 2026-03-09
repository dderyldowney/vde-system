#!/usr/bin/env zsh
# Unit Tests for vde-templates Library
# Tests template rendering and VM creation functions

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
# TEST SETUP
# =============================================================================

TEST_TMPDIR=""

setup_test_env() {
    export VDE_TEST_MODE=1

    TEST_TMPDIR="/tmp/vde-templates-test-$$"
    mkdir -p "$TEST_TMPDIR"
    export HOME="$TEST_TMPDIR/home"
    mkdir -p "$HOME/.ssh/vde"
    mkdir -p "$TEST_TMPDIR/templates"
    mkdir -p "$TEST_TMPDIR/configs/docker"
    mkdir -p "$TEST_TMPDIR/cache"

    # Export paths for testing
    export VDE_ROOT_DIR="$PROJECT_ROOT"
    export VDE_TEMPLATES_DIR="$TEST_TMPDIR/templates"
    export VDE_CONFIGS_DIR="$TEST_TMPDIR/configs/docker"
    
    # Force reload libraries
    unset _VDE_SHELL_COMPAT_LOADED _VDE_CONSTANTS_LOADED _VDE_ERRORS_LOADED _VDE_TEMPLATES_LOADED 2>/dev/null
    
    source "$PROJECT_ROOT/lib/vde-shell-compat"
    source "$PROJECT_ROOT/lib/vde-constants"
    source "$PROJECT_ROOT/lib/vde-errors"
    source "$PROJECT_ROOT/lib/vde-templates"
}

teardown_test_env() {
    rm -rf "$TEST_TMPDIR"
}

# =============================================================================
# TESTS: TEMPLATE RENDERING
# =============================================================================

test_render_template() {
    test_start "render_template - single variable"

    setup_test_env
    local template_file="$VDE_TEMPLATES_DIR/test1.tmpl"
    cat > "$template_file" << 'EOF'
Hello {{NAME}}!
EOF

    local result
    result=$(render_template "$template_file" "NAME" "World" 2>/dev/null)
    if [[ "$result" == "Hello World!" ]]; then
        test_pass "render_template - single variable"
    else
        test_fail "render_template - single variable" "Got: $result"
    fi

    test_start "render_template - multiple variables"
    local template_file2="$VDE_TEMPLATES_DIR/test2.tmpl"
    cat > "$template_file2" << 'EOF'
Hello {{NAME}}, welcome to {{PLACE}}!
EOF

    result=$(render_template "$template_file2" "NAME" "Alice" "PLACE" "VDE" 2>/dev/null)
    if [[ "$result" == "Hello Alice, welcome to VDE!" ]]; then
        test_pass "render_template - multiple variables"
    else
        test_fail "render_template - multiple variables" "Got: $result"
    fi

    teardown_test_env
}

test_create_vm_from_template() {
    test_start "create_vm_from_template - creates VM directory"

    setup_test_env
    cat > "$VDE_TEMPLATES_DIR/custom.tmpl" << 'EOF'
version: '3.8'
services:
  {{VM_NAME}}:
    image: custom/image:latest
EOF

    if create_vm_from_template "custom" "vde-my-vm" 2>/dev/null; then
        if [[ -f "$VDE_CONFIGS_DIR/vde-my-vm/docker-compose.yml" ]]; then
            test_pass "create_vm_from_template - creates VM directory"
        else
            test_fail "create_vm_from_template - creates VM directory" "File not created in $VDE_CONFIGS_DIR/vde-my-vm"
        fi
    else
        test_fail "create_vm_from_template - creates VM directory" "Command failed"
    fi

    teardown_test_env
}

test_create_vm_from_template_renders_vars() {
    test_start "create_vm_from_template - renders variables"

    setup_test_env
    cat > "$VDE_TEMPLATES_DIR/custom.tmpl" << 'EOF'
version: '3.8'
services:
  {{VM_NAME}}:
    image: {{IMAGE}}
EOF

    create_vm_from_template "custom" "vde-my-vm" "IMAGE" "test/image:v1.0" 2>/dev/null

    local result
    result=$(cat "$VDE_CONFIGS_DIR/vde-my-vm/docker-compose.yml" 2>/dev/null)
    if echo "$result" | grep -q "test/image:v1.0"; then
        test_pass "create_vm_from_template - renders variables"
    else
        test_fail "create_vm_from_template - renders variables" "Image not found in: $result"
    fi

    teardown_test_env
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

echo "=============================================="
echo "VDE Templates Library Unit Tests (Consistent Naming)"
echo "=============================================="
echo ""

test_render_template
test_create_vm_from_template
test_create_vm_from_template_renders_vars

echo ""
echo "=============================================="
echo "Test Summary"
echo "=============================================="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed"
    exit 1
fi
