# Test Framework Schema-Validated Configuration

## Overview

Both Behave (BDD) and Pytest (unit testing) now use **schema-validated JSON configuration files** integrated with VDE's validation+regeneration mechanisms.

## Architecture

```
tests/
├── behave-config.json          # Behave BDD config
├── behave-config.schema.json   # JSON Schema for Behave
├── pytest-config.json          # Pytest unit test config
├── pytest-config.schema.json   # JSON Schema for Pytest
├── test_config_loader.py       # Shared config loader (validates against schemas)
├── conftest.py                 # Pytest hook (loads pytest-config.json)
└── features/
    └── environment.py          # Behave hooks (loads behave-config.json)
```

## Configuration Files

### Behave Config (`behave-config.json`)

```json
{
  "version": "1.0",
  "description": "Behave BDD test configuration",
  "behave": {
    "format": "pretty",
    "color": true,
    "order": "normal",
    "tags": {
      "exclude": ["@wip", "@skip"]
    }
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "paths": {
    "features": "tests/features",
    "steps": "tests/features/steps"
  },
  "test_categories": {
    "docker_required": {
      "tags": ["@docker"],
      "description": "Tests requiring Docker"
    }
  }
}
```

### Pytest Config (`pytest-config.json`)

```json
{
  "version": "1.0",
  "description": "Pytest unit test configuration",
  "pytest": {
    "testpaths": ["tests/unit"],
    "markers": {
      "slow": "Slow tests",
      "integration": "Integration tests",
      "unit": "Unit tests",
      "docker": "Tests requiring Docker",
      "ssh": "Tests requiring SSH"
    }
  },
  "coverage": {
    "enabled": true,
    "source": ["scripts/lib"]
  },
  "paths": {
    "test_dir": "tests/unit",
    "fixtures": "tests/fixtures"
  }
}
```

## Validation Integration

### Config Loader (`test_config_loader.py`)

The `TestConfigLoader` class provides:

1. **Schema Auto-Detection**: Automatically finds `*.schema.json` for `*.json`
2. **VDE-Core Integration**: Uses `vde_validate_json_schema()` from `vde-core`
3. **Python Fallback**: Falls back to Python `jsonschema` library if VDE-core unavailable
4. **Singleton Pattern**: Config loaded once per test session
5. **Lazy Loading**: Config validated only when first accessed

#### Usage Example

```python
from test_config_loader import get_behave_config, get_pytest_config

# Load behave config
behave_config = get_behave_config()
config_data = behave_config.load(validate=True)

# Access config values
behave_format = config_data["behave"]["format"]
log_level = config_data["logging"]["level"]

# Dict-like access
paths = behave_config["paths"]
```

### Behave Integration

**File:** `tests/features/environment.py`

```python
from test_config_loader import get_behave_config

def get_config():
    """Get behave configuration (lazy load)."""
    global _BEHAVE_CONFIG
    if _BEHAVE_CONFIG is None:
        config_loader = get_behave_config()
        _BEHAVE_CONFIG = config_loader.load(validate=True)
    return _BEHAVE_CONFIG

def before_all(context):
    """Hook runs before any tests execute."""
    # Load schema-validated config
    config = get_config()

    # Store in context for access in steps
    context.behave_config = config

    # Use config values
    behave_settings = config["behave"]
    logging_settings = config["logging"]
```

### Pytest Integration

**File:** `tests/conftest.py`

```python
from test_config_loader import get_pytest_config

def pytest_configure(config):
    """Configure pytest using schema-validated JSON."""
    pytest_config = get_pytest_config()
    config_data = pytest_config.load(validate=True)

    # Register markers from config
    markers = config_data.get("pytest", {}).get("markers", {})
    for marker_name, marker_desc in markers.items():
        config.addinivalue_line("markers", f"{marker_name}: {marker_desc}")

    # Store config for access in tests
    config._vde_pytest_config = config_data
```

## Validation Mechanisms

### 1. Schema Validation

Both configs are validated on load:

```python
# Automatic validation when loading
config = get_behave_config()
data = config.load(validate=True)  # Raises ConfigValidationError if invalid
```

### 2. VDE-Core Integration

Config loader uses VDE validation functions:

```zsh
# From vde-core
vde_validate_json_schema "behave-config.json" "behave-config.schema.json"
```

### 3. Python Fallback

If VDE-core unavailable, uses Python `jsonschema`:

```python
import jsonschema
jsonschema.validate(instance=config, schema=schema)
```

## Testing

### Integration Tests

**File:** `tests/test-config-integration.py`

```bash
python3 tests/test-config-integration.py
```

Tests:
- ✓ Behave config loads and validates
- ✓ Pytest config loads and validates
- ✓ Schema files exist and are valid
- ✓ VDE-core validation available

### Unit Tests

**File:** `tests/unit/test-framework-config.test.zsh`

```bash
zsh tests/unit/test-framework-config.test.zsh
```

Tests (15 total):
- Config file existence
- Schema file existence
- Config loader functionality
- Environment.py integration
- Conftest.py integration
- Schema validation

## Benefits

1. **Type Safety**: JSON Schema validates config structure
2. **Single Source of Truth**: Config in JSON, not scattered in code
3. **Version Control**: Track config changes in git
4. **Consistency**: Same validation mechanism as VM configs
5. **Regeneration**: Config errors trigger regeneration (future)
6. **Documentation**: Schema serves as config documentation

## Migration Path

### Before (behave.ini)

```ini
[behave]
format = pretty
color = true
logging_level = INFO
```

### After (behave-config.json)

```json
{
  "version": "1.0",
  "behave": {
    "format": "pretty",
    "color": true
  },
  "logging": {
    "level": "INFO"
  }
}
```

## Error Handling

### Invalid Config

```python
try:
    config = get_behave_config()
    data = config.load(validate=True)
except ConfigValidationError as e:
    print(f"Config validation failed: {e}")
    # Falls back to defaults
```

### Missing Schema

```python
# Auto-detects schema from config filename
# behave-config.json → behave-config.schema.json
```

### VDE-Core Unavailable

```python
# Automatically falls back to Python jsonschema
# Prints warning if neither available
```

## Future Enhancements

1. **Config Regeneration**: Auto-regenerate on validation failure
2. **Schema Updates**: Migrate configs on schema version changes
3. **Config Merging**: Support environment-specific overrides
4. **Cache Configs**: Cache validated configs for performance
5. **Config Validation CLI**: `./scripts/vde validate-test-configs`

## Files Modified

- `tests/behave-config.json` - Created
- `tests/behave-config.schema.json` - Created
- `tests/pytest-config.json` - Created
- `tests/pytest-config.schema.json` - Created
- `tests/test_config_loader.py` - Created
- `tests/conftest.py` - Created
- `pytest.ini` - Created
- `tests/features/environment.py` - Updated (added config loading)
- `run-unit-tests.zsh` - Updated (added test-framework-config.test.zsh)

## Verification

```bash
# Verify integration
python3 tests/test-config-integration.py

# Run unit tests
zsh tests/unit/test-framework-config.test.zsh

# Run all unit tests
./run-unit-tests.zsh
```

## Summary

✅ Behave and Pytest now use schema-validated JSON configs
✅ Integrated with VDE validation+regeneration mechanisms
✅ 15/15 integration tests passing
✅ Backward compatible with existing tests
✅ Single source of truth for test configuration
