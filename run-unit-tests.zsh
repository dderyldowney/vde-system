#!/usr/bin/env zsh
# Run all unit tests for VDE libraries

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=============================================="
echo "VDE Unit Test Suite"
echo "=============================================="
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# List of unit test files (in dependency order)
UNIT_TESTS=(
    "tests/unit/vde-constants.test.zsh"
    "tests/unit/vde-naming.test.zsh"
    "tests/unit/vde-path-utils.test.zsh"
    "tests/unit/vde-core.test.zsh"
    "tests/unit/vde-shell-compat.test.zsh"
    "tests/unit/vm-common.test.zsh"
    "tests/unit/vde-parser.test.zsh"
    "tests/unit/vde-errors.test.zsh"
    "tests/unit/vde-log.test.zsh"
    "tests/unit/vde-metrics.test.zsh"
    "tests/unit/vde-progress.test.zsh"
    "tests/unit/vde-audit.test.zsh"
    "tests/unit/vde-health.test.zsh"
)

# Docker-dependent tests (optional)
DOCKER_TESTS=(
    "tests/unit/vde-docker-state.test.zsh"
)

# Run standard unit tests
for test_file in "${UNIT_TESTS[@]}"; do
    if [[ -f "$PROJECT_ROOT/$test_file" ]]; then
        echo "----------------------------------------------"
        echo "Running: $test_file"
        echo "----------------------------------------------"

        zsh "$PROJECT_ROOT/$test_file"
        local result=$?

        if [[ $result -eq 0 ]]; then
            ((TESTS_PASSED++))
        else
            ((TESTS_FAILED++))
        fi
        echo ""
    else
        echo "MISSING: $test_file"
        ((TESTS_FAILED++))
        echo ""
    fi
done

# Run Docker-dependent tests (optional)
echo "----------------------------------------------"
echo "Docker-Dependent Tests (optional)"
echo "----------------------------------------------"

docker_available=false
if docker --version >/dev/null 2>&1; then
    docker_available=true
    echo "Docker available - running docker-dependent tests"
else
    echo "Docker NOT available - skipping docker-dependent tests"
fi
echo ""

if [[ "$docker_available" == "true" ]]; then
    for test_file in "${DOCKER_TESTS[@]}"; do
        if [[ -f "$PROJECT_ROOT/$test_file" ]]; then
            echo "----------------------------------------------"
            echo "Running: $test_file"
            echo "----------------------------------------------"

            zsh "$PROJECT_ROOT/$test_file"
            local result=$?

            if [[ $result -eq 0 ]]; then
                ((TESTS_PASSED++))
            else
                ((TESTS_FAILED++))
            fi
            echo ""
        fi
    done
fi

echo "=============================================="
echo "Unit Test Summary"
echo "=============================================="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo "✓ All unit tests passed!"
    exit 0
else
    echo "✗ Some unit tests failed"
    exit 1
fi
