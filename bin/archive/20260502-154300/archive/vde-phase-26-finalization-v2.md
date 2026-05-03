# Implementation Plan: VDE Phase 26 Finalization (v2)
<!-- @shared-law (Forge Component) -->

**Objective**: Remediate Network Isolation bypass and Error Map misalignment discovered during Phase 26 regression.

## Background & Motivation
Phase 26 regression revealed 8 failing BDD scenarios. Diagnosis confirmed:
1. **Network Isolation Bypass**: `bin/vde` is missing the `--network` flag in `docker run`.
2. **Error Map Conflict**: `vde_error_map` is using hardcoded codes (5, 6) that conflict with `vde-constants`.

## Key Files & Context
- `bin/vde`: Core CLI logic for VM ignition.
- `lib/vde-errors`: Centralized error handling and signal translation.
- `lib/vde-constants`: Authoritative source for return codes.

## Implementation Steps

### 1. Network Isolation & Error Correction (bin/vde)
- **Action**: Fix network creation error mapping and enforce container network isolation.
- **Changes**:
  - In `bin/vde`, change `vde_error_map ${VDE_ERR_DOCKER:-5} "network create"` to `vde_error_map ${VDE_ERR_DOCKER:-8} "network create"`.
  - In `bin/vde`, change `exit ${VDE_ERR_DOCKER:-5}` to `exit ${VDE_ERR_DOCKER:-8}`.
  - In `bin/vde`, update `docker run` to include `--network "${net_name}"`.

### 2. Error Map Alignment (lib/vde-errors)
- **Action**: Align `vde_error_map` with `vde-constants`.
- **Changes**:
  - Map `5` (VDE_ERR_TIMEOUT) to `vde_error_ssh_connection_failed`.
  - Map `6` (VDE_ERR_EXISTS) to `vde_error_container_exists`.
  - Map `8` (VDE_ERR_DOCKER) to `vde_error_docker_build_failed`.

## Verification & Testing

### 1. Manual Verification
- **Test 1**: Run `export VDE_DOCKER_NETWORK="invalid!name" && vde start python`.
- **Expected**: Failure with "Error: Failed to create Docker network".

### 2. Regression Run (BDD)
- **Action**: Run `behave tests/features/core-infrastructure/error-handling.feature`.
- **Expected**: **16 Scenarios Passed (100%)**.

### 3. Compliance Check
- **Action**: Run `bin/vde-enforce-uap.zsh`.
- **Expected**: **PASS (CLEAN)**.

## Rollback Plan
- Revert changes via `git checkout bin/vde lib/vde-errors`.
- Restore the original Error Map from session start.
