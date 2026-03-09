#!/usr/bin/env zsh
# Unit Tests for vde-docker Library
# Tests Docker container management functions

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

    TEST_TMPDIR="/tmp/vde-docker-test-$$"
    mkdir -p "$TEST_TMPDIR"
    export HOME="$TEST_TMPDIR/home"
    mkdir -p "$HOME/.ssh/vde"
    mkdir -p "$TEST_TMPDIR/cache"
    mkdir -p "$TEST_TMPDIR/port-registry"

    # Export paths for testing
    export VDE_ROOT_DIR="$PROJECT_ROOT"
    export VDE_CONFIGS_DIR="$TEST_TMPDIR/configs/docker"
    export CONFIGS_DIR="$VDE_CONFIGS_DIR"
    export VDE_CACHE_DIR="$TEST_TMPDIR/cache"
    export VDE_PORT_REGISTRY="$TEST_TMPDIR/port-registry"
    export VDE_HOME_DIR="$HOME"
    
    mkdir -p "$VDE_CONFIGS_DIR"

    # Unset guards
    unset _VDE_SHELL_COMPAT_LOADED _VDE_CONSTANTS_LOADED _VDE_NAMING_LOADED \
          _VDE_PATH_UTILS_LOADED _VDE_CORE_GUARD_LOADED _VM_COMMON_LOADED \
          _VDE_DOCKER_LOADED 2>/dev/null

    source "$PROJECT_ROOT/lib/vde-shell-compat"
    source "$PROJECT_ROOT/lib/vde-constants"
    source "$PROJECT_ROOT/lib/vde-naming"
    source "$PROJECT_ROOT/lib/vde-path-utils"
    source "$PROJECT_ROOT/lib/vde-core"
    source "$PROJECT_ROOT/lib/vm-common"
    source "$PROJECT_ROOT/lib/vde-docker"
}

teardown_test_env() {
    rm -rf "$TEST_TMPDIR"
}

# =============================================================================
# TESTS: COMPOSE FILE FUNCTIONS
# =============================================================================

test_get_compose_file() {
    test_start "get_compose_file (raw name lookup)"

    setup_test_env
    mkdir -p "$VDE_CONFIGS_DIR/python"
    cat > "$VDE_CONFIGS_DIR/python/docker-compose.yml" << 'EOF'
version: '3.8'
services:
  vde-python:
    image: vde-python:latest
EOF

    # Test lookup with raw name
    local result
    result=$(get_compose_file "python" 2>/dev/null)
    if [[ "$result" == "$VDE_CONFIGS_DIR/python/docker-compose.yml" ]]; then
        test_pass "get_compose_file (raw)"
    else
        test_fail "get_compose_file (raw)" "Wrong path: $result"
        return
    fi

    # Test lookup with prefixed name (should still find it via normalization)
    result=$(get_compose_file "vde-python" 2>/dev/null)
    if [[ "$result" == "$VDE_CONFIGS_DIR/python/docker-compose.yml" ]]; then
        test_pass "get_compose_file (prefixed)"
    else
        test_fail "get_compose_file (prefixed)" "Wrong path: $result"
    fi

    teardown_test_env
}

test_get_docker_project_name() {
    test_start "get_docker_project_name"

    # From raw name
    local result
    result=$(get_docker_project_name "python" 2>/dev/null)
    if [[ "$result" == "vde-python" ]]; then
        test_pass "get_docker_project_name (raw)"
    else
        test_fail "get_docker_project_name (raw)" "Got: $result"
        return
    fi

    # From prefixed name (idempotent)
    result=$(get_docker_project_name "vde-python" 2>/dev/null)
    if [[ "$result" == "vde-python" ]]; then
        test_pass "get_docker_project_name (prefixed)"
    else
        test_fail "get_docker_project_name (prefixed)" "Got: $result"
    fi
}

# =============================================================================
# RUN ALL TESTS
# =============================================================================

echo "=============================================="
echo "VDE Docker Library Unit Tests (Mixed Naming)"
echo "=============================================="
echo ""

# Check if Docker is available — print clearly, don't silently fail
DOCKER_AVAILABLE=0
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    DOCKER_AVAILABLE=1
    echo "[INFO] Docker daemon is available — running all tests"
else
    echo "[SKIP] Docker daemon not available — running mock-only tests"
    echo "       (Start Docker and re-run to include live container tests)"
fi
echo ""

test_get_compose_file
test_get_docker_project_name

echo ""
echo "=============================================="
echo "Test Summary"
echo "=============================================="
echo "Passed:  $TESTS_PASSED"
echo "Failed:  $TESTS_FAILED"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed"
    exit 1
fi
