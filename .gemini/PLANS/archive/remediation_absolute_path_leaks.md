# Remediation Plan: Absolute Path Leak Purification
<!-- @forge (Governance Sentinel) -->

## Objective
Remediate the [CRITICAL] Protocol Fracture detected by the UAP Enforcer in `plans/scripts/test_fifo.zsh`. Purge all hardcoded absolute paths to ensure workspace portability and security.

## Identified Violations
- **File**: `plans/scripts/test_fifo.zsh`
- **Leaked Paths**:
    - `source ".../VDE/lib/vm-common"`
    - `source ".../VDE/lib/vde-core"`
    - `source ".../VDE/lib/vm-lock"`
    - `>> ".../VDE/plans/scripts/fifo_test.log"`

## Remediation Steps
1.  **Purge Absolute Paths**: Replace all instances of hardcoded VDE root paths with `${VDE_ROOT_DIR}/` in `plans/scripts/test_fifo.zsh`.
2.  **Verify Portability**: Ensure `VDE_ROOT_DIR` is correctly derived within the script or inherited from the environment.
3.  **Audit Reset**: Rerun `bin/vde-enforce-uap.zsh` to certify the fix.

## Verification
- `bin/vde-enforce-uap.zsh` must return **PASS (CLEAN)**.
