# Beskar-Steel Trap Implementation Plan (VDE v2.0.6)
<!-- @armor (Engine Core) -->

## 1. lib/vm-common Update
- **save_port_to_registry(vm, port)**:
  - Create `${VDE_CACHE_DIR}/port-registry/port-${port}.lock/PID` containing $$.
- **find_available_port(min, max)**:
  - In loop, if `mkdir` lock fails:
    - Check for stale lock: `kill -0 $(cat lock/PID)`.
    - If dead, `rm -rf` lock and retry `mkdir`.
  - Use `lsof -nP -i :${port}` for host check.
  - On success, write PID to lock.
- **release_port(port)**:
  - Ensure `rm -rf` the entire lock directory.

## 2. bin/vde Update
- In `start)` block:
  - Define `local ALLOCATED_PORT`.
  - Add `trap '[[ -n "${ALLOCATED_PORT}" ]] && release_port_reservation "${ALLOCATED_PORT}"' EXIT`.
  - Set `ALLOCATED_PORT` after `allocate_port_for_vm`.
  - Unset `ALLOCATED_PORT` after successful `docker run`.

## 3. bin/add-vm-type Update
- Audit `always` block. Ensure it executes and handles exit gracefully.

## 4. Verification
- Clean Sweep:
  - `bin/shutdown-all all -f`
  - `rm -rf .cache/port-registry/*`
  - `rm -rf .locks/vms/*`
- Run test:
  - `bin/vde-enforce-uap.zsh behave tests/features/core-infrastructure/concurrency-stress.feature`
