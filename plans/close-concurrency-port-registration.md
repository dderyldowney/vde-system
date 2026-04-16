# Close Concurrency and Port Registration Plan

## Goal
To close the oldest plan (`plans/scripts/2026-03-25-fix-concurrency-and-port-registration.md`) by implementing its outstanding task (Task 2) and formally archiving it, thereby hardening the Forge against "Thundering Herd" race conditions during port allocation.

## Background & Motivation
An audit of `plans/scripts/2026-03-25-fix-concurrency-and-port-registration.md` revealed that while Task 1 is obsolete (due to the purging of `docker-compose.yml`), Task 2 remains unaddressed. Currently, in `bin/add-vm-type`, the `find_available_ssh_port` command executes *before* `claim_lock` is acquired. In highly concurrent scenarios, this allows multiple processes to be assigned the same port before the registry is safely locked.

## Implementation Steps

### 1. Refactor `bin/add-vm-type` (Atomic Port Allocation)
- **Target**: `bin/add-vm-type`
- **Action**: Move the following block from lines 164-169 into the atomic lock block (after `claim_lock "${global_lock}" || vde_handle_error ...`):
  ```zsh
  if [[ -z "${SSH_PORT}" ]]; then
      log_info "No SSH port specified, auto-allocating..."
      SSH_PORT=$(find_available_ssh_port 2200 2299 "${QUIET}")
      vde_handle_error "port-allocation" "${VM_NAME}"
      log_success "Allocated port: ${SSH_PORT}"
  fi
  ```

### 2. Empirical Verification (The Gauntlet)
- **Action**: Execute a clean sweep and run the concurrency stress tests to certify the fix under load.
- **Commands**:
  ```zsh
  bin/vde stop all
  rm -rf .cache/port-registry/* .locks/vms/*
  python3 -m behave tests/features/core-infrastructure/concurrency-stress.feature
  ```

### 3. Archival (The Pruning Ritual)
- **Action**: Move the completed plan to the archive to maintain a lean Forge.
- **Command**:
  ```zsh
  mv plans/scripts/2026-03-25-fix-concurrency-and-port-registration.md plans/archive/scripts/
  ```

## Verification
- `bin/vde-enforce-uap.zsh` must exit with code 0.
- `concurrency-stress.feature` must report 100% pass rate.
- The legacy plan file must no longer exist in `plans/scripts/`.