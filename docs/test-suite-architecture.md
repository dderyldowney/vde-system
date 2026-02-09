# VDE Test Suite Architecture

## Overview

The VDE test suite uses a **hybrid approach** with both **Zsh tests** and **Pytest tests**, all using **schema-validated JSON configuration**.

## Test Types

### Zsh Unit Tests (Must Remain Zsh)

**Purpose:** Test zsh-specific functionality that cannot be tested via subprocess

**When to use:**
- Testing associative arrays
- Testing zsh variable behavior
- Testing source guards and library loading
- Testing zsh-specific syntax/features
- Testing shell script performance

**Location:** `tests/unit/*.test.zsh`

**Config:** Uses `load-test-config.zsh` to read `pytest-config.json`

**Examples:**
- `vde-constants.test.zsh` - Tests zsh constants and variable exports
- `vde-shell-compat.test.zsh` - Tests shell compatibility features
- Tests that verify associative array population

**Pattern:**
```zsh
#!/usr/bin/env zsh

# Load test config (reads pytest-config.json)
source "$(dirname "$0")/../lib/load-test-config.zsh"

# Get timeout from config
TIMEOUT=$(get_test_timeout "function")

# Run tests...
```

### Pytest Unit Tests (Converted from Zsh)

**Purpose:** Test VDE functionality via subprocess (doesn't require zsh internals)

**When to use:**
- Testing validation functions
- Testing JSON parsing
- Testing configuration loading
- Testing error handling
- Testing return codes and outputs

**Location:** `tests/unit/test_*.py`

**Config:** Uses `test_config_loader.py` to read `pytest-config.json`

**Examples:**
- `test_vde_validation.py` - Tests validation functions via subprocess
- Future: `test_vde_commands.py` - Tests VDE CLI commands

**Pattern:**
```python
import pytest
from test_config_loader import get_pytest_config

# Load config
pytest_config = get_pytest_config()
config_data = pytest_config.load(validate=True)

@pytest.fixture
def test_timeout():
    timeout_config = config_data.get("timeout", {})
    return timeout_config.get("default", 60)

def test_something(test_timeout):
    result = subprocess.run([...], timeout=test_timeout)
    assert result.returncode == 0
```

### Behave Integration Tests (BDD)

**Purpose:** Test complete workflows and user scenarios

**When to use:**
- Testing multi-step workflows
- Testing Docker container operations
- Testing SSH functionality
- Testing end-to-end scenarios
- Testing user-facing features

**Location:** `tests/features/*.feature`

**Config:** Uses `test_config_loader.py` to read `behave-config.json`

**Examples:**
- `vm-lifecycle.feature` - Tests VM creation, start, stop, destroy
- `docker-operations.feature` - Tests Docker operations
- `ssh-and-remote-access.feature` - Tests SSH workflows

## Configuration Architecture

```
tests/
├── pytest-config.json              # Schema-validated config
├── pytest-config.schema.json       # JSON Schema
├── behave-config.json              # Schema-validated config
├── behave-config.schema.json       # JSON Schema
├── test_config_loader.py           # Python config loader
├── lib/
│   └── load-test-config.zsh       # Zsh config loader
├── unit/
│   ├── *.test.zsh                 # Zsh unit tests (zsh-specific)
│   └── test_*.py                  # Pytest unit tests (converted)
└── features/
    ├── *.feature                  # Behave BDD tests
    └── environment.py             # Loads behave-config.json
```

## Config Loading by Test Type

| Test Type | Config File | Loader | Settings Used |
|-----------|-------------|--------|---------------|
| Zsh unit tests | pytest-config.json | load-test-config.zsh | timeout, verbosity |
| Pytest unit tests | pytest-config.json | test_config_loader.py | timeout, markers, coverage |
| Behave BDD tests | behave-config.json | test_config_loader.py | format, logging, paths |

## Decision Matrix: Zsh vs Pytest

| Test Focus | Technology | Reason |
|------------|-----------|---------|
| Associative arrays | Zsh | Requires zsh internals |
| Source guards | Zsh | Tests library loading |
| Variable exports | Zsh | Tests shell environment |
| Shell syntax | Zsh | Zsh-specific features |
| Validation functions | Pytest | Can test via subprocess |
| JSON parsing | Pytest | Python has better JSON tools |
| Return codes | Pytest | Can test via subprocess |
| Error messages | Pytest | Can capture stderr easily |
| Configuration loading | Pytest | Can test via subprocess |
| CLI commands | Pytest | Can test via subprocess |
| Multi-step workflows | Behave | BDD scenarios |
| Docker operations | Behave | Integration testing |

## Migration Strategy

### Phase 1: Foundation (Complete ✓)
- ✓ Create pytest-config.json + schema
- ✓ Create behave-config.json + schema
- ✓ Create test_config_loader.py (Python)
- ✓ Create load-test-config.zsh (Zsh)
- ✓ Integrate with behave environment.py
- ✓ Create pytest conftest.py

### Phase 2: Convert Suitable Tests (In Progress)
- ✓ Identify which tests can be converted to pytest
- ✓ Create test_vde_validation.py as example
- ☐ Convert validation tests to pytest
- ☐ Convert parsing tests to pytest
- ☐ Convert configuration tests to pytest
- ☐ Update run-unit-tests.zsh to run both zsh and pytest

### Phase 3: Update Remaining Zsh Tests
- ☐ Update zsh tests to use load-test-config.zsh
- ☐ Apply timeout settings from config
- ☐ Apply verbosity settings from config
- ☐ Standardize test output format

### Phase 4: Documentation
- ✓ Document test architecture
- ☐ Document migration guidelines
- ☐ Update contributor guide

## Running Tests

### All Tests
```bash
# Run all tests (zsh + pytest + behave)
./run-all-tests.zsh
```

### Zsh Unit Tests Only
```bash
# Run zsh unit tests
zsh run-unit-tests.zsh
```

### Pytest Unit Tests Only
```bash
# Run pytest tests
pytest tests/unit/test_*.py -v
```

### Behave Integration Tests
```bash
# Run all behave tests
cd tests && behave

# Run specific feature
cd tests && behave features/vm-lifecycle.feature

# Run with tag filter
cd tests && behave --tags=@docker
```

### Verify Config Integration
```bash
# Test config loading
python3 tests/test-config-integration.py

# Verify zsh config loader
zsh tests/lib/load-test-config.zsh && echo "Config loaded: timeout=$TEST_TIMEOUT_DEFAULT"
```

## Test Markers (Pytest)

From `pytest-config.json`:
- `@pytest.mark.slow` - Slow tests (can skip with `-m "not slow"`)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.docker` - Requires Docker
- `@pytest.mark.ssh` - Requires SSH

## Test Categories (Behave)

From `behave-config.json`:
- `@docker` - Requires Docker environment
- `@no-docker` - Runs without Docker
- `@ssh` - SSH-related tests
- `@workflow` - Complete workflow tests
- `@wip` - Work in progress (excluded by default)

## Benefits of Hybrid Approach

✅ **Best of Both Worlds:**
- Zsh tests: Direct access to shell internals, fast, accurate
- Pytest tests: Better assertions, fixtures, tooling, coverage

✅ **Single Source of Truth:**
- All tests read from schema-validated JSON configs
- Consistent timeout, verbosity, coverage settings

✅ **Appropriate Technology:**
- Use zsh tests where zsh internals needed
- Use pytest where subprocess testing sufficient
- Use behave for BDD workflows

✅ **Gradual Migration:**
- No big-bang rewrite required
- Convert tests incrementally
- Both approaches coexist

## Examples

### Zsh Test with Config

```zsh
#!/usr/bin/env zsh
# tests/unit/vde-arrays.test.zsh

source "$(dirname "$0")/../lib/load-test-config.zsh"
source "$PROJECT_ROOT/scripts/lib/vm-common"

# Get timeout from config
TIMEOUT=$(get_test_timeout "function")

# Test associative arrays (requires zsh)
test_vm_names_array() {
    if [[ ${#VM_NAMES[@]} -eq 0 ]]; then
        echo "✗ VM_NAMES array is empty"
        return 1
    fi
    echo "✓ VM_NAMES array has ${#VM_NAMES[@]} entries"
    return 0
}

test_vm_names_array
```

### Pytest Test with Config

```python
# tests/unit/test_vde_cli.py

import subprocess
from test_config_loader import get_pytest_config

pytest_config = get_pytest_config()
config = pytest_config.load(validate=True)

def test_vde_list_command():
    timeout = config["timeout"]["default"]

    result = subprocess.run(
        ["./scripts/vde", "list"],
        capture_output=True,
        text=True,
        timeout=timeout
    )

    assert result.returncode == 0
    assert "python" in result.stdout  # Should list python VM
```

## Summary

- **Zsh tests** - For zsh-specific internals (associative arrays, source guards, etc.)
- **Pytest tests** - For testable-via-subprocess functionality (validation, parsing, CLI)
- **Behave tests** - For BDD workflows (Docker, SSH, multi-step scenarios)
- **All tests** - Use schema-validated JSON configs for consistency
