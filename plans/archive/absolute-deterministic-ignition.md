# Absolute Deterministic Ignition Plan
<!-- @shared-law (Forge Component) -->

## Objective
Apply the Section 10 "Physical Handshake" (Docker Probe) discipline to all port allocation authorities and harden the global locking mechanism to achieve 100% deterministic success under concurrent load.

## Key Files & Context
- `lib/vde-ssh`: Contains `acquire_lock` (Global Locking).
- `lib/vde-docker`: Contains `find_available_ssh_port` (Port Allocation).
- `lib/vm-common`: Contains `find_available_port` and `vde_acquire_global_lock`.

## Implementation Steps

### 1. Harden `acquire_lock` in `lib/vde-ssh`
- Implement atomic `pid_file` creation to avoid race conditions where a concurrent process reads an empty or partial PID file.
- Use the `mv` trick for atomic filesystem operations.
- Ensure the re-entrancy check is robust.

### 2. Standardize & Harden Port Allocation
- Update `find_available_ssh_port` in `lib/vde-docker` to use the **Docker Probe** (Physical Handshake).
- Unify probe container naming: `vde-port-probe-${port}` to allow parallel probes for different ports.
- Ensure all port allocation functions respect Section 10.

### 3. Harden `vde_acquire_global_lock` in `lib/vm-common`
- Ensure the stagger is robust and re-entrancy is handled.

## Verification
- Re-run the full concurrency stress suite:
```zsh
bin/vde stop --all && \
rm -rf .cache/port-registry/* .locks/vms/* && \
python3 -m behave tests/features/core-infrastructure/concurrency-stress.feature
```
- Expectation: 100% PASS for all scenarios.
