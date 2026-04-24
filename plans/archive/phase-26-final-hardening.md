# Phase 26 Final Hardening Strike Plan
<!-- @shared-law (Forge Component) -->

## Objective
Implement `lib/vm-lock` with the "Registry Retry Ritual" (Staggered Jitter 0.1s-0.5s, 10-attempt limit, `mkdir` atomicity) and update all registry operations to use it.

## Key Files & Context
- `lib/vm-lock` (New): Centralized atomic file-locking library.
- `lib/vde-ssh`: Remove old `acquire_lock` and `release_lock` (or update to use `lib/vm-lock`).
- `lib/vm-common`: Source `lib/vm-lock` and ensure port allocation is Section 10 compliant.
- `bin/add-vm-type` / `lib/vde-core` (Registry Operations): Wrap writes to `.conf` and `.json` in the "Registry Retry Ritual".

## Implementation Steps

### 1. Create `lib/vm-lock`
```zsh
#!/usr/bin/env zsh
# VDE Atomic File Locking Library

if [[ "${_VM_LOCK_LOADED:-}" = "1" ]]; then
    return 0 2>/dev/null || exit 0
fi
_VM_LOCK_LOADED=1

# Global state for recursive locking
typeset -gA VDE_LOCK_DEPTH

# vde_acquire_lock - Atomic locking with "Registry Retry Ritual"
# Args: <lock_file> [timeout_seconds]
# Features: 10-attempt limit, 0.1s-0.5s Staggered Jitter, mkdir atomicity
vde_acquire_lock() {
    local lock_file="${1}"
    local max_attempts=10
    local attempt=1
    local pid_file="${lock_file}/pid"

    # RE-ENTRANCY CHECK
    if [[ "${VDE_LOCK_DEPTH[${lock_file}]}" -gt 0 ]]; then
        (( VDE_LOCK_DEPTH[${lock_file}]++ ))
        return 0
    fi

    mkdir -p "$(dirname "${lock_file}")" 2>/dev/null

    while [[ ${attempt} -le ${max_attempts} ]]; do
        # ATOMIC ENTRY GATE
        if mkdir "${lock_file}" 2>/dev/null; then
            # Record ownership
            local now=$(date +%s)
            local pgid=$(ps -o pgid= -p $$ 2>/dev/null | tr -d ' ')
            local tmp_pid_file="${pid_file}.tmp.$RANDOM"
            echo "$$:${pgid}:${now}" > "${tmp_pid_file}" 2>/dev/null
            mv "${tmp_pid_file}" "${pid_file}" 2>/dev/null
            
            VDE_LOCK_DEPTH[${lock_file}]=1
            return 0
        fi
        
        # Staggered Jitter (0.1s - 0.5s)
        local jitter_ms=$(( (RANDOM % 400) + 100 ))
        local jitter_sec=$(( jitter_ms / 1000.0 ))
        "${VDE_ROOT_DIR}/bin/vde-poll" --wait "${jitter_sec}" "all" >/dev/null 2>&1
        
        (( attempt++ ))
    done

    vde_log_error "Failed to acquire lock after ${max_attempts} attempts: ${lock_file}"
    return ${VDE_ERR_LOCK:-9}
}

vde_release_lock() {
    local lock_file="${1}"
    if [[ -n "${VDE_LOCK_DEPTH[${lock_file}]}" ]]; then
        (( VDE_LOCK_DEPTH[${lock_file}]-- ))
        if [[ "${VDE_LOCK_DEPTH[${lock_file}]}" -le 0 ]]; then
            [[ -d "${lock_file}" ]] && rm -rf "${lock_file}" 2>/dev/null
            unset "VDE_LOCK_DEPTH[${lock_file}]"
        fi
    else
        [[ -d "${lock_file}" ]] && rm -rf "${lock_file}" 2>/dev/null
    fi
    return 0
}
```

### 2. Refactor Sovereignty
- Source `lib/vm-lock` in `lib/vm-common` and `lib/vde-core`.
- Replace calls to `acquire_lock` and `release_lock` with `vde_acquire_lock` and `vde_release_lock`.
- Remove legacy lock implementations from `lib/vde-ssh` and `lib/vm-common` (`vde_acquire_global_lock`).
- Ensure `find_available_ssh_port` and `find_available_port` adhere strictly to Section 10 Docker Probe handshakes (already completed in previous steps, but will verify).

### 3. Verify the Fix
- Run the final strike sequence:
```zsh
bin/vde stop all && \
rm -rf .cache/port-registry/* .locks/vms/* && \
python3 -m behave tests/features/core-infrastructure/concurrency-stress.feature
```
- Run `bin/vde-enforce-uap.zsh` for final certification.
