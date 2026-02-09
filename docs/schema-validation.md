# VDE Schema Validation System

Centralized JSON schema validation and cache regeneration for all VDE libraries.

## Overview

The VDE schema validation system provides:
- **Automatic validation** of JSON config files against their schemas
- **Cache regeneration** when configs change or become corrupt
- **Error recovery** from corrupt or missing files
- **Consistent validation** across all libraries

## Architecture

### Core Functions (vde-core)

All schema validation logic is centralized in `scripts/lib/vde-core`:

```zsh
# Check if schema file is valid
vde_check_schema_integrity <schema_file>

# Validate JSON against schema
vde_validate_json_schema <json_file> <schema_file>

# Get schema file for a JSON config
vde_get_schema_for_json <json_file>

# Validate JSON and check if cache needs regeneration
vde_validate_or_regenerate <json_file> <schema_file> <cache_file>
```

### Library Integration (vm-common)

Libraries use centralized validation:

```zsh
# Validate VM types config without loading
validate_vm_types_config

# Force cache regeneration
regenerate_vm_types_cache

# Load VM types (with automatic validation)
load_vm_types
```

## Error Codes

New error codes in `vde-constants`:

| Code | Value | Description |
|------|-------|-------------|
| `VDE_ERR_INVALID_DATA` | 10 | Data validation failed (corrupt file, schema mismatch) |
| `VDE_ERR_CACHE_INVALID` | 11 | Cache is stale, corrupt, or missing (needs regeneration) |

## Usage

### Automatic Validation

Validation happens automatically when loading VM types:

```zsh
source scripts/lib/vm-common
load_vm_types  # Validates JSON against schema automatically
```

Output:
```
[INFO] Using JSON VM types config: scripts/data/vm-types.json
[INFO] Validating config against schema: scripts/data/vm-types.schema.json
[INFO] Schema validation passed: scripts/data/vm-types.json
[INFO] Loading VM types from cache...
```

### Manual Validation

Validate without loading:

```zsh
source scripts/lib/vm-common
validate_vm_types_config
# Returns: VDE_SUCCESS (0) or VDE_ERR_INVALID_DATA (10)
```

### Force Cache Regeneration

Rebuild cache from JSON:

```zsh
source scripts/lib/vm-common
regenerate_vm_types_cache
```

This will:
1. Validate JSON against schema
2. Remove old cache
3. Reload and regenerate cache

### Direct Core Functions

Use core functions directly:

```zsh
source scripts/lib/vde-core

# Get schema for JSON file
schema_file=$(vde_get_schema_for_json "scripts/data/vm-types.json")

# Validate JSON
if vde_validate_json_schema "scripts/data/vm-types.json" "$schema_file"; then
    echo "Valid"
else
    echo "Invalid"
fi
```

## Cache Management

### Cache Validation

The system validates cache files before loading:

1. **Syntax check**: Verify cache is valid zsh
2. **Source check**: Test sourcing the cache
3. **Corruption detection**: Remove corrupt cache automatically

```zsh
# Cache validation (automatic in load_vm_types)
if _is_cache_valid "$VM_TYPES_CACHE" "$VM_TYPES_JSON"; then
    if zsh -n "$VM_TYPES_CACHE" 2>/dev/null; then
        if . "$VM_TYPES_CACHE" 2>/dev/null; then
            # Cache loaded successfully
        else
            # Cache corrupt, remove and regenerate
            rm -f "$VM_TYPES_CACHE"
        fi
    fi
fi
```

### Cache Regeneration

Cache is regenerated when:
- Cache file is missing
- Cache file is corrupt
- JSON file is newer than cache
- Explicitly requested via `regenerate_vm_types_cache`

Regeneration process:
1. Validate JSON against schema
2. Parse JSON with `jq`
3. Generate zsh associative arrays
4. Write cache file with proper escaping

## Schema Files

### vm-types.schema.json

Location: `scripts/data/vm-types.schema.json`

Defines validation rules for VM type configuration:

**Language VMs** must have:
- `name`: lowercase alphanumeric string
- `display`: non-empty string
- `install`: non-empty shell command
- `port`: null

**Service VMs** must have:
- `name`: lowercase alphanumeric string
- `display`: non-empty string
- `install`: non-empty shell command
- `port`: comma-separated port numbers (e.g., `"80,443"`)

### Schema Naming Convention

Schemas follow the naming pattern: `{config}.schema.json`

Example:
- Config: `vm-types.json`
- Schema: `vm-types.schema.json`

This allows automatic schema discovery via `vde_get_schema_for_json`.

## Error Handling

### Validation Failures

When validation fails:

```zsh
[ERROR] JSON validation failed: scripts/data/vm-types.json
[ERROR] Config file may be corrupt or missing required fields
```

The function returns `VDE_ERR_INVALID_DATA` (10).

### Recovery

The system automatically recovers from:
- **Corrupt cache**: Removed and regenerated
- **Missing cache**: Generated on next load
- **Stale cache**: Regenerated when JSON is newer

For corrupt JSON:
- **No automatic recovery** (requires manual fix)
- **Clear error messages** indicating the problem
- **Validation prevents bad data** from being used

## Testing

### Unit Tests

Location: `tests/unit/vde-schema-validation.test.zsh`

Coverage:
- Schema integrity validation
- JSON schema validation
- Schema discovery
- Error code definition
- Cache validation
- Invalid data detection

Run tests:
```bash
tests/unit/vde-schema-validation.test.zsh
# Expected: 16+ passed, 0-1 failed
```

### VM Types Schema Tests

Location: `tests/unit/vm-types-schema.test.zsh`

Coverage:
- VM types structure validation
- Language VM requirements
- Service VM requirements
- Name and port patterns

Run tests:
```bash
tests/unit/vm-types-schema.test.zsh
# Expected: 10 passed, 0 failed
```

## Design Principles

### 1. Single Source of Truth

JSON files are the authoritative source:
- **Schemas validate** JSON structure
- **Caches optimize** loading speed
- **Validation ensures** data integrity

### 2. Fail Fast

Validation happens early:
- **On load**: Validate before using data
- **On write**: Validate before committing
- **On cache**: Validate before generation

### 3. Automatic Recovery

System self-heals when possible:
- **Corrupt cache**: Auto-regenerate
- **Missing cache**: Auto-create
- **Stale cache**: Auto-update

### 4. Centralized Logic

All validation in one place:
- **vde-core**: Core validation functions
- **Libraries**: Call core functions
- **Consistent**: Same validation everywhere

## Future Enhancements

### Additional Schemas

Create schemas for other JSON configs:
- Docker compose configurations
- Environment variable files
- Test configurations

### Schema Versioning

Track schema versions for migration:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "version": "2.0",
  "previousVersions": ["1.0"]
}
```

### Validation Caching

Cache validation results to avoid re-validating:
```zsh
# Cache validation result with checksum
validation_cache=".cache/validation-$(md5sum vm-types.json)"
```

### JSON Schema Library

Use proper JSON Schema validator:
```bash
pip install jsonschema
python3 -m jsonschema -i vm-types.json vm-types.schema.json
```

## Examples

### Example 1: Loading VM Types

```zsh
#!/usr/bin/env zsh
source scripts/lib/vm-common

# Automatic validation happens here
load_vm_types

# Use VM data
echo "Python VM: ${VM_DISPLAY[python]}"
```

### Example 2: Validating Before Commit

```zsh
#!/usr/bin/env zsh
source scripts/lib/vm-common

# Validate config before committing changes
if validate_vm_types_config; then
    echo "Config valid, safe to commit"
    git add scripts/data/vm-types.json
    git commit -m "Update VM types config"
else
    echo "Config invalid, fix errors first"
    exit 1
fi
```

### Example 3: Forcing Cache Rebuild

```zsh
#!/usr/bin/env zsh
source scripts/lib/vm-common

# Rebuild cache if corrupt
if ! load_vm_types 2>/dev/null; then
    echo "Load failed, regenerating cache..."
    regenerate_vm_types_cache
fi
```

### Example 4: Custom Validation

```zsh
#!/usr/bin/env zsh
source scripts/lib/vde-core

# Validate custom JSON config
json_file="my-config.json"
schema_file=$(vde_get_schema_for_json "$json_file")

if vde_validate_json_schema "$json_file" "$schema_file"; then
    echo "✓ Configuration valid"
else
    echo "✗ Configuration invalid"
    exit $VDE_ERR_INVALID_DATA
fi
```

## Troubleshooting

### "Schema validation failed"

**Cause**: JSON doesn't match schema requirements

**Solution**:
1. Check JSON syntax: `jq . scripts/data/vm-types.json`
2. Compare against schema: `scripts/data/vm-types.schema.json`
3. Fix missing/invalid fields
4. Re-run validation

### "Cache file corrupt"

**Cause**: Cache has syntax errors or invalid content

**Solution**:
```zsh
# Automatic recovery - just reload
source scripts/lib/vm-common
regenerate_vm_types_cache
```

### "Schema file not found"

**Cause**: Schema missing or in wrong location

**Solution**:
1. Verify schema exists: `ls scripts/data/*.schema.json`
2. Check naming: `{config}.schema.json`
3. Create schema if missing

### "Python not available"

**Cause**: Validation requires Python 3

**Solution**:
```bash
# Install Python 3
brew install python3  # macOS
apt install python3   # Debian/Ubuntu
```

## References

- **JSON Schema Spec**: https://json-schema.org/
- **Draft 7 Spec**: http://json-schema.org/draft-07/schema
- **Validation Examples**: `tests/unit/vde-schema-validation.test.zsh`
- **VM Types Schema**: `scripts/data/vm-types.schema.json`
