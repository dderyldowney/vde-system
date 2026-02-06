# Plan 30: Technical Debt Reduction - COMPLETED

## Executive Summary

**Status:** COMPLETE

**Review Date:** February 6, 2026

**Note:** Plan 29 (SSH Configuration) is blocked with 108 undefined steps in `ssh-configuration.feature`. SSH tests require infrastructure dependencies.

## Current Status (February 6, 2026)

### Infrastructure Fix Verified

**FIXED:** `container_exists()` function added to `scripts/lib/vm-common` and used by `vde-commands`.
- `vde create` now correctly checks container existence instead of config existence
- Tests can delete containers and recreate them without errors

### Docker-Free Tests
- **Features:** 6 passed, 0 failed
- **Scenarios:** 135 passed, 0 failed
- **Steps:** 560 passed, 0 failed

### Related Plans
- **Plan 31:** IN PROGRESS - Error handling feature (72 undefined steps)
- **Plan 32:** PENDING - SSH configuration (108 undefined steps) - LARGEST SINGLE WIN

## Test Results Summary

### Unit Tests
- **vde-parser.test.zsh:** 27 passed, 0 failed

### Docker-Free Tests (After Fix)
- **Features:** 6 passed, 0 failed
- **Scenarios:** 135 passed, 0 failed
- **Steps:** 560 passed, 0 failed

---

## Debug Analysis: State-Related Scenario Failures

### Root Causes Identified

**Issue 1: Alias Matching (FIXED)**
- Tests expected "postgresql" but parser returned "postgres" (canonical)
- Fixed by modifying `step_plan_should_include_vm` to handle aliases

**Issue 2: Display Names Not Recognized (FIXED)**
- Tests use "JavaScript" (display name) but parser only recognizes canonical/aliases
- Parser recognized: js, node, nodejs
- Parser did NOT recognize: JavaScript (display name only)
- **FIXED:** Modified `_build_alias_map` to include display names (lowercase) in VM_ALIAS_MAP

### VM Naming Convention (from vm-types.conf)

| Canonical | Aliases | Display Name |
|----------|---------|--------------|
| postgres | postgresql | PostgreSQL |
| js | node, nodejs | JavaScript |
| python | py, python3 | Python |
| go | golang | Go |

**Parser now matches:** canonical names, aliases, AND display names (converted to lowercase).

### Failures After Fix (0 total)

All display name issues resolved. SSH tests may still fail without Docker infrastructure.

---

## Remediation Options

### FIXED: Extend Parser to Support Display Names

Modified `_build_alias_map` in `scripts/lib/vde-parser` to also include display names (in lowercase) in the VM_ALIAS_MAP. This allows natural language inputs like "JavaScript" to be correctly matched to the canonical VM name "js".

```zsh
# Also add display name (in lowercase) to support natural language like "JavaScript"
local display_name
display_name=$(get_vm_info display "$vm" 2>/dev/null)
if [ -n "$display_name" ]; then
    local display_lower
    display_lower=$(echo "$display_name" | tr '[:upper:]' '[:lower:]')
    _assoc_set "VM_ALIAS_MAP" "$display_lower" "$vm"
fi
```

---

## Files Modified

| File | Change |
|------|--------|
| `tests/features/steps/documented_workflow_steps.py` | Fixed alias matching, added 13 missing steps |
| `tests/features/environment.py` | Added VDE_DOCKER_FREE_TEST mode |
| `scripts/lib/vde-parser` | Added display name support to `_build_alias_map` |

## Related Work

### Plan 31: Error Handling (In Progress)
- Core VDE fix: `vde create` now checks container existence, not config existence
- Added `container_exists()` function to vm-common
- Fixed `validate_vm_doesnt_exist()` and `vde_vm_exists()`

### Plan 32: SSH Configuration (Next)
- **Largest single win:** 108 undefined steps in `ssh-configuration.feature`
- Requires Docker infrastructure (now fixed by Plan 31)

## Run Tests

```bash
# Unit tests
./tests/unit/vde-parser.test.zsh

# Docker-free tests
VDE_DOCKER_FREE_TEST=1 python3 -m behave tests/features/docker-free/ --format=plain
```

## Git History

- `36e97c2` - fix: resolve duplicate step definitions
- `b3b7684` - feat: add VDE_DOCKER_FREE_TEST mode
- `35d4237` - docs: verify step files exist
- `a83a521` - docs: add debug analysis and remediation plan
- **[LATEST]** - fix: add display name support to vde-parser alias map
