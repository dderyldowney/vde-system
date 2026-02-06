# Plan 31: Error Handling & Recovery Remediation

## Executive Summary

**Status:** IN PROGRESS - Step Definitions Phase (Infrastructure FIXED)

**Feature:** `tests/features/docker-required/error-handling-and-recovery.feature`

**Scope:** 72 undefined steps + 14 errors

## Infrastructure Status

**FIXED:** `container_exists()` function added to `scripts/lib/vm-common` and `scripts/lib/vde-commands`.
- `vde create` now correctly checks container existence instead of config existence
- Test infrastructure can delete and recreate containers without errors

## Root Cause: Container vs Config Confusion

**Problem:** VDE scripts checked for CONFIG existence, not CONTAINER existence:
- `vm_exists()` checks if `configs/docker/<vm>/docker-compose.yml` exists
- `vde create` would skip creation if config exists, even if container doesn't
- This broke test infrastructure that deletes containers but keeps configs

**Solution:** Check container existence instead of config

## Changes Made

### 1. Added `container_exists()` function (scripts/lib/vm-common)
New function that checks if container exists (running or stopped):
```zsh
container_exists() {
    local vm=$1
    local container_name
    local vm_type
    vm_type=$(_assoc_get "VM_TYPE" "$vm" 2>/dev/null)
    if [ "$vm_type" = "lang" ]; then
        container_name="${vm}-dev"
    else
        container_name="$vm"
    fi
    if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qx "$container_name"; then
        return $VDE_SUCCESS
    fi
    return $VDE_ERR_NOT_FOUND
}
```

### 2. Updated `vde_vm_exists()` (scripts/lib/vde-commands)
Changed from calling `vm_exists()` (config) to `container_exists()` (container)

### 3. Updated `validate_vm_doesnt_exist()` (scripts/lib/vm-common)
Changed to check container existence instead of config

## Verification

```bash
# Before fix: vde create python → "VM 'python' already exists (config found at:...)"
# After fix: vde create python → Proceeds to create container
docker rm -f python-dev && ./scripts/vde create python  # Now works!
```

## Files Modified

| File | Change |
|------|--------|
| `scripts/lib/vm-common` | Added `container_exists()`, fixed `validate_vm_doesnt_exist()` |
| `scripts/lib/vde-commands` | Fixed `vde_vm_exists()` to use `container_exists()` |
| `tests/features/environment.py` | Removed `docker rm -f` fallback, now raises error |
| `tests/features/steps/test_utilities.py` | Removed `docker rm -f` fallback, now raises error |

## Current Phase: Step Definitions

72 undefined steps need implementation. The infrastructure is ready.

### Step Definitions Needed (72 undefined)

Categorize by step type:

| Step Type | Count | Examples |
|-----------|-------|----------|
| Given | ~20 | given VM is in error state, given recovery is triggered |
| When | ~25 | when error occurs, when recovery mechanism runs |
| Then | ~27 | then system recovers, then error is logged |

---

## Files Involved

- `tests/features/docker-required/error-handling-and-recovery.feature`
- `tests/features/steps/error_handling_steps.py` (may need creation)
- `tests/features/environment.py` (error context setup)

---

## Implementation Strategy

### Phase 1: Error Context Setup (COMPLETED)
- Infrastructure fix complete

### Phase 2: Error Detection Steps (PENDING)
- Implement `When` steps for triggering error scenarios
- Use error injection patterns

### Phase 3: Recovery Validation (PENDING)
- Implement `Then` steps for verifying recovery behavior
- Validate error logging and notification

---

## Run Tests

```bash
# Dry run to see current state
python3 -m behave tests/features/docker-required/error-handling-and-recovery.feature --dry-run

# Full run with verbose output
python3 -m behave tests/features/docker-required/error-handling-and-recovery.feature -v
```
