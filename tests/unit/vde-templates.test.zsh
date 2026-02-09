#!/usr/bin/env zsh
# Unit Tests for vde-templates Library
# Tests template rendering and VM creation functions

# Don't use set -e as it interferes with test counting

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$PROJECT_ROOT/scripts/lib/vde-shell-compat"
source "$PROJECT_ROOT/scripts/lib/vde-constants"
source "$PROJECT_ROOT/scripts/lib/vde-errors"
source "$PROJECT_ROOT/scripts/lib/vde-templates"

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
    TEST_TMPDIR="/tmp/vde-templates-test-$$"
    mkdir -p "$TEST_TMPDIR"
    export HOME="$TEST_TMPDIR/home"
    mkdir -p "$HOME/.ssh/vde"
    mkdir -p "$TEST_TMPDIR/templates"
    mkdir -p "$TEST_TMPDIR/configs/docker"
    mkdir -p "$TEST_TMPDIR/cache"

    # Override paths for testing
    export VDE_TEMPLATES_DIR="$TEST_TMPDIR/templates"
    export VDE_CONFIG_DIR="$TEST_TMPDIR/configs/docker"
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
    local template_file="$TEST_TMPDIR/templates/test1.tmpl"
    cat > "$template_file" << 'EOF'
Hello {{NAME}}!
EOF

    local result
    result=$(render_template "$template_file" "NAME" "World" 2>/dev/null)
    if [ "$result" = "Hello World!" ]; then
        test_pass "render_template - single variable"
    else
        test_fail "render_template - single variable" "Got: $result"
    fi

    test_start "render_template - multiple variables"
    local template_file2="$TEST_TMPDIR/templates/test2.tmpl"
    cat > "$template_file2" << 'EOF'
Hello {{NAME}}, welcome to {{PLACE}}!
EOF

    result=$(render_template "$template_file2" "NAME" "Alice" "PLACE" "VDE" 2>/dev/null)
    if [ "$result" = "Hello Alice, welcome to VDE!" ]; then
        test_pass "render_template - multiple variables"
    else
        test_fail "render_template - multiple variables" "Got: $result"
    fi

    test_start "render_template - non-existent file"
    if ! render_template "/nonexistent/path.tmpl" "NAME" "test" 2>/dev/null; then
        test_pass "render_template - non-existent file"
    else
        test_fail "render_template - non-existent file" "Expected failure"
    fi

    teardown_test_env
}

test_render_template_string() {
    test_start "render_template_string - template string"

    local result
    result=$(render_template_string "Hello {{NAME}}!" "NAME" "Test" 2>/dev/null)
    if [ "$result" = "Hello Test!" ]; then
        test_pass "render_template_string - template string"
    else
        test_fail "render_template_string - template string" "Got: $result"
    fi
}

# =============================================================================
# TESTS: TEMPLATE UTILITIES
# =============================================================================

test_list_templates() {
    test_start "list_templates - lists templates"

    setup_test_env
    touch "$VDE_TEMPLATES_DIR/template1.tmpl"
    touch "$VDE_TEMPLATES_DIR/template2.tmpl"
    touch "$VDE_TEMPLATES_DIR/readme.txt"

    local result
    result=$(list_templates 2>/dev/null)
    if echo "$result" | grep -q "template1" && echo "$result" | grep -q "template2"; then
        test_pass "list_templates - lists templates"
    else
        test_fail "list_templates - lists templates" "Got: $result"
    fi

    teardown_test_env
}

test_template_exists() {
    test_start "template_exists - template exists"

    setup_test_env
    touch "$VDE_TEMPLATES_DIR/existing.tmpl"

    if template_exists "existing" 2>/dev/null; then
        test_pass "template_exists - template exists"
    else
        test_fail "template_exists - template exists" "Expected true"
    fi

    test_start "template_exists - template does not exist"
    if ! template_exists "nonexistent" 2>/dev/null; then
        test_pass "template_exists - template does not exist"
    else
        test_fail "template_exists - template does not exist" "Expected false"
    fi

    teardown_test_env
}

test_get_template_file() {
    test_start "get_template_file - returns correct path"

    setup_test_env
    touch "$VDE_TEMPLATES_DIR/my-template.tmpl"

    local result
    result=$(get_template_file "my-template" 2>/dev/null)
    if [ "$result" = "$VDE_TEMPLATES_DIR/my-template.tmpl" ]; then
        test_pass "get_template_file - returns correct path"
    else
        test_fail "get_template_file - returns correct path" "Got: $result"
    fi

    teardown_test_env
}

# =============================================================================
# TESTS: VARIABLE EXTRACTION
# =============================================================================

test_extract_template_vars() {
    test_start "extract_template_vars - extracts variables"

    setup_test_env
    local template_file="$TEST_TMPDIR/templates/vars.tmpl"
    cat > "$template_file" << 'EOF'
Hello {{NAME}}, your email is {{EMAIL}}.
Your ID is {{ID_NUMBER}}.
EOF

    local result
    result=$(extract_template_vars "$template_file" 2>/dev/null)
    if echo "$result" | grep -q "NAME" && echo "$result" | grep -q "EMAIL" && echo "$result" | grep -q "ID_NUMBER"; then
        test_pass "extract_template_vars - extracts variables"
    else
        test_fail "extract_template_vars - extracts variables" "Got: $result"
    fi

    teardown_test_env
}

test_extract_template_vars_no_vars() {
    test_start "extract_template_vars - no variables"

    setup_test_env
    local template_file="$TEST_TMPDIR/templates/no-vars.tmpl"
    echo "Hello World!" > "$template_file"

    local result
    result=$(extract_template_vars "$template_file" 2>/dev/null)
    if [ -z "$result" ]; then
        test_pass "extract_template_vars - no variables"
    else
        test_fail "extract_template_vars - no variables" "Got: $result"
    fi

    teardown_test_env
}

# =============================================================================
# TESTS: VM CREATION FROM TEMPLATES
# =============================================================================

test_create_vm_from_template() {
    test_start "create_vm_from_template - creates VM directory"

    setup_test_env
    cat > "$VDE_TEMPLATES_DIR/custom.tmpl" << 'EOF'
version: '3.8'
services:
  {{VM_NAME}}:
    image: custom/image:latest
EOF

    if create_vm_from_template "custom" "my-vm" 2>/dev/null; then
        if [ -f "$VDE_CONFIG_DIR/my-vm/docker-compose.yml" ]; then
            test_pass "create_vm_from_template - creates VM directory"
        else
            test_fail "create_vm_from_template - creates VM directory" "File not created"
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

    create_vm_from_template "custom" "my-vm" "IMAGE" "test/image:v1.0" 2>/dev/null

    local result
    result=$(cat "$VDE_CONFIG_DIR/my-vm/docker-compose.yml")
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
echo "VDE Templates Library Unit Tests"
echo "=============================================="
echo ""

test_render_template
test_render_template_string
test_list_templates
test_template_exists
test_get_template_file
test_extract_template_vars
test_extract_template_vars_no_vars
test_create_vm_from_template
test_create_vm_from_template_renders_vars

echo ""
echo "=============================================="
echo "Test Summary"
echo "=============================================="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed"
    exit 1
fi
