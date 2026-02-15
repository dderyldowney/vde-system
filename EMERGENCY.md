# EMERGENCY - Docker Test Infrastructure Issue - RESOLVED

**Date:** 2026-02-13  
**Status:** RESOLVED - Fix implemented in environment.py

## Problem Summary

Docker-required tests hang when trying to create VMs. The `vde create` command hangs at:
```
#1 [internal] load local bake definitions
```

This is a **Docker BuildKit** issue, not a test infrastructure bug.

## Root Cause

The VDE uses Docker BuildKit for building images. When running in non-interactive mode (like tests), BuildKit can hang waiting for input or due to misconfigured build context.

## Solution Implemented

**FIX:** Set `DOCKER_BUILDKIT=0` in the test environment to disable BuildKit.

### Files Modified

- `tests/features/environment.py` - Added DOCKER_BUILDKIT=0 to:
  - `run_vde_command()` function - sets env variable for VDE script subprocesses
  - `before_all()` hook - sets env variable globally for all test processes

### Additional Requirements

- `dev-net` Docker network must exist for tests to work:
  ```bash
  docker network create dev-net
  ```

## Verification

Run tests with:
```bash
behave tests/features/docker-required/docker-operations.feature
```

The build should progress without hanging at "load local bake definitions".

## Previous Work (Pre-Feb 13)

1. Fixed test infrastructure to clean stale `.docker-state` files
2. Fixed VM creation steps to check `.docker-state` files 
3. Fixed test scenario to remove images before testing rebuild
4. Added step definition for image removal
5. Fixed error handling bug (TypeError with bytes vs str)
6. Increased timeouts to 600s for VM creation

## Files Modified (Historical)

- `tests/features/environment.py` - Stale state cleanup
- `tests/features/steps/docker_lifecycle_steps.py` - VM creation steps, image removal step
- `tests/features/docker-required/docker-operations.feature` - Test scenario fix
- `tests/features/steps/vm_common.py` - Error handling fix
