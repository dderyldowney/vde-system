# Neutralize the "Thundering Herd" on the Global Config
<!-- @shared-law (Forge Component) -->

## Objective
Update the registry logic to include a "Staggered Retry" (randomized initial delay and robust jittered backoff) for the `global-config.lock` to prevent the "Thundering Herd" effect during parallel operations.

## Key Files & Context
- `lib/vm-common` (or wherever `acquire_lock` is most relevant, currently in `lib/vde-ssh`)
- `lib/vde-core`: Contains `vde_translate_conf_to_json` which uses the global lock.
- `bin/add-vm-type`: CLI tool that uses the global lock.

## Proposed Solution
1. Introduce a helper function `vde_acquire_global_lock` in `lib/vm-common` that implements a randomized initial stagger before calling the standard `acquire_lock`.
2. Update `bin/add-vm-type` and `vde_translate_conf_to_json` in `lib/vde-core` to use `vde_acquire_global_lock`.
3. Enhance the `acquire_lock` jitter in `lib/vde-ssh` if necessary to ensure it's sufficiently randomized.

## Implementation Plan

### Step 1: Add `vde_acquire_global_lock` to `lib/vm-common`
```zsh
vde_acquire_global_lock() {
    local lock_file="${VDE_LOCKS_DIR}/global-config.lock"
    local timeout="${1:-60}"
    
    # THE SEEKER'S STAGGER (Rule 10 Enhancement)
    # Randomized initial delay (0-1500ms) to break the "Thundering Herd" alignment
    local initial_jitter=$(( RANDOM % 1500 ))
    local jitter_sec=$(( initial_jitter / 1000.0 ))
    "${VDE_ROOT_DIR}/bin/vde-poll" --wait "${jitter_sec}" "all" >/dev/null 2>&1
    
    acquire_lock "${lock_file}" "${timeout}"
}
```

### Step 2: Update `bin/add-vm-type`
Replace:
```zsh
acquire_lock "${global_lock}" 60
vde_handle_error "lock-acquisition" "${global_lock}"
```
With:
```zsh
vde_acquire_global_lock 60 || vde_handle_error "lock-acquisition" "${global_lock}"
```

### Step 3: Update `lib/vde-core`
Update `vde_translate_conf_to_json` to use `vde_acquire_global_lock`.

## Verification
Re-run the concurrency stress test:
```zsh
bin/vde stop --all && \
rm -rf .cache/port-registry/* .locks/vms/* && \
python3 -m behave tests/features/core-infrastructure/concurrency-stress.feature
```
Expectation: Both scenarios pass.
