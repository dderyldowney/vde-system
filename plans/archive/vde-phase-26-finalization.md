# Plan: Phase 26 Finalization — Error Engine & UX Hardening (Revised)

## Objective
Finalize Phase 26 by implementing robust signal translation and enhancing concurrency transparency. NO SIMULATION. ACTUAL IMPLEMENTATION ONLY.

## Key Files & Context
- `lib/vde-errors`: Centralized error mapping.
- `lib/vde-ssh`: Core locking logic (`acquire_lock`).
- `bin/vde`: CLI entry point.

## Implementation Steps

### 1. Error Engine: Signal Translation (ACTUAL)
- Update `vde_error_map` in `lib/vde-errors` to explicitly handle exit codes 130 (SIGINT), 137 (SIGKILL), and 143 (SIGTERM).
- Provide concrete remediation for each:
    - 130: "Operation interrupted by user."
    - 137: "Process forcefully terminated. Check system resources (OOM) or Docker daemon health."
    - 143: "Termination signal received. Check for conflicting system management processes."

### 2. Lock Contention Transparency (ACTUAL)
- Modify `vde_progress_wait_for_lock` in `lib/vde-progress` to accept owner info (PID/PGID).
- Update `acquire_lock` in `lib/vde-ssh` to read the PID file and pass its content to the progress indicator.
- Display: "Waiting for lock: <name> (Held by PID <pid>)".

### 3. UX Polish & Consistency
- Audit `bin/vde` to ensure `vde_progress_spinner` wraps all `docker build` and `docker run` calls.
- Verify `vde-poll` is used for all health/readiness checks.

## Verification & Testing (ACTUAL)
1. **Port Contention Test**:
    - Trigger a background `vde start` that holds a lock.
    - Run a foreground `vde start` and verify it displays the PID of the background process.
2. **Signal Interception Test**:
    - Run `vde rebuild python`.
    - Manually send `kill -SIGINT` to the process.
    - Verify the output matches the new error mapping.
3. **Regression**: Rerun `tests/features/core-infrastructure/error-handling.feature`.

## Migration & Rollback
- No schema changes.
- Rollback: Revert library files to previous state.
