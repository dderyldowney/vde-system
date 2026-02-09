#!/usr/bin/env zsh
# Unit tests for test framework schema-validated config integration

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source test utilities
source "$PROJECT_ROOT/tests/lib/test-utils.zsh" 2>/dev/null || {
    # Define minimal test functions if test-utils.zsh not available
    test_suite_start() { echo "=== $1 ===" }
    test_assert() {
        if eval "$1" 2>/dev/null; then
            echo "✓ $2"
            return 0
        else
            echo "✗ $2"
            return 1
        fi
    }
    test_suite_end() { echo "" }
}

test_suite_start "Test Framework Config Integration Tests"

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Behave config file exists
if test_assert "[ -f '$PROJECT_ROOT/tests/behave-config.json' ]" \
    "Behave config file exists"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 2: Behave schema file exists
if test_assert "[ -f '$PROJECT_ROOT/tests/behave-config.schema.json' ]" \
    "Behave schema file exists"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 3: Pytest config file exists
if test_assert "[ -f '$PROJECT_ROOT/tests/pytest-config.json' ]" \
    "Pytest config file exists"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 4: Pytest schema file exists
if test_assert "[ -f '$PROJECT_ROOT/tests/pytest-config.schema.json' ]" \
    "Pytest schema file exists"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 5: Config loader module exists
if test_assert "[ -f '$PROJECT_ROOT/tests/test_config_loader.py' ]" \
    "Config loader module exists"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 6: Pytest conftest.py exists
if test_assert "[ -f '$PROJECT_ROOT/tests/conftest.py' ]" \
    "Pytest conftest.py exists"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 7: Pytest.ini exists
if test_assert "[ -f '$PROJECT_ROOT/pytest.ini' ]" \
    "pytest.ini exists"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test 8: Behave environment.py imports config loader
if grep -q "from test_config_loader import get_behave_config" \
    "$PROJECT_ROOT/tests/features/environment.py"; then
    echo "✓ Behave environment.py imports config loader"
    ((TESTS_PASSED++))
else
    echo "✗ Behave environment.py missing config loader import"
    ((TESTS_FAILED++))
fi

# Test 9: Behave environment.py uses get_config()
if grep -q "get_config()" "$PROJECT_ROOT/tests/features/environment.py"; then
    echo "✓ Behave environment.py uses get_config()"
    ((TESTS_PASSED++))
else
    echo "✗ Behave environment.py doesn't call get_config()"
    ((TESTS_FAILED++))
fi

# Test 10: Config loader can load behave config
if python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/tests')
from test_config_loader import get_behave_config
config = get_behave_config()
data = config.load(validate=True)
assert 'version' in data
assert 'behave' in data
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo "✓ Config loader can load and validate behave config"
    ((TESTS_PASSED++))
else
    echo "✗ Config loader failed to load behave config"
    ((TESTS_FAILED++))
fi

# Test 11: Config loader can load pytest config
if python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/tests')
from test_config_loader import get_pytest_config
config = get_pytest_config()
data = config.load(validate=True)
assert 'version' in data
assert 'pytest' in data
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo "✓ Config loader can load and validate pytest config"
    ((TESTS_PASSED++))
else
    echo "✗ Config loader failed to load pytest config"
    ((TESTS_FAILED++))
fi

# Test 12: Behave config has required fields
if python3 -c "
import sys, json
sys.path.insert(0, '$PROJECT_ROOT/tests')
with open('$PROJECT_ROOT/tests/behave-config.json') as f:
    data = json.load(f)
assert 'version' in data
assert 'behave' in data
assert 'logging' in data
assert 'paths' in data
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo "✓ Behave config has all required fields"
    ((TESTS_PASSED++))
else
    echo "✗ Behave config missing required fields"
    ((TESTS_FAILED++))
fi

# Test 13: Pytest config has required fields
if python3 -c "
import sys, json
sys.path.insert(0, '$PROJECT_ROOT/tests')
with open('$PROJECT_ROOT/tests/pytest-config.json') as f:
    data = json.load(f)
assert 'version' in data
assert 'pytest' in data
assert 'paths' in data
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo "✓ Pytest config has all required fields"
    ((TESTS_PASSED++))
else
    echo "✗ Pytest config missing required fields"
    ((TESTS_FAILED++))
fi

# Test 14: Behave config validates against schema
if python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/tests')
from test_config_loader import TestConfigLoader
from pathlib import Path
config = TestConfigLoader(
    Path('$PROJECT_ROOT/tests/behave-config.json'),
    Path('$PROJECT_ROOT/tests/behave-config.schema.json')
)
config.load(validate=True)
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo "✓ Behave config validates against schema"
    ((TESTS_PASSED++))
else
    echo "✗ Behave config schema validation failed"
    ((TESTS_FAILED++))
fi

# Test 15: Pytest config validates against schema
if python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/tests')
from test_config_loader import TestConfigLoader
from pathlib import Path
config = TestConfigLoader(
    Path('$PROJECT_ROOT/tests/pytest-config.json'),
    Path('$PROJECT_ROOT/tests/pytest-config.schema.json')
)
config.load(validate=True)
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo "✓ Pytest config validates against schema"
    ((TESTS_PASSED++))
else
    echo "✗ Pytest config schema validation failed"
    ((TESTS_FAILED++))
fi

test_suite_end

echo "=============================================="
echo "Test Framework Config Integration Test Results"
echo "=============================================="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo ""
    echo "✓ All test framework config integration tests passed!"
    exit 0
else
    echo ""
    echo "✗ Some tests failed"
    exit 1
fi
