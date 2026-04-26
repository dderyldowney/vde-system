# Remediation Plan for Infinite Recursion Loop in Locking Mechanism

## 1. Rule Record Locations
- `bin/vde-poll` (Sections 2, 4, 4.5)
- `lib/vm-common` (Section: VM TYPE LOADING, around line 200)

## 2. Exact Text Updated

### `bin/vde-poll`
**Old Text (Top of file):**
```zsh
# --- 2. SOURCE CORE ECOSYSTEM ---
if [[ -f "${VDE_ROOT_DIR}/lib/vm-common" ]]; then
    source "${VDE_ROOT_DIR}/lib/vm-common"
else
    echo "CRITICAL: lib/vm-common not found."
    exit ${VDE_ERR_GENERAL}
fi
```

**New Text (Moved below Section 4.5):**
```zsh
# --- 4. ARGUMENT PARSING ---
zmodload zsh/zutil
typeset -A opts
zparseopts -D -A opts -health -port: -exec: -network: -state: -count: -timeout: -interval: -wait:

VM_NAME="$1"
[[ -z "${VM_NAME}" && -z "${opts[--network]}" && -z "${opts[--count]}" && -z "${opts[--wait]}" ]] && show_usage && exit ${VDE_ERR_INVALID_INPUT:-2}

TIMEOUT=${opts[--timeout]:-30}
INTERVAL=${opts[--interval]:-0.2}

# --- 4.5 FIXED WAIT STRIKE ---
if [[ -n "${opts[--wait]}" ]]; then
    echo "[INFO] [poll] Executing fixed wait: ${opts[--wait]}s (Jitter/Stagger Mandate)..."
    # Convert seconds to deciseconds for zselect -t
    # Use floating point math via zsh built-in $(( ))
    local wait_ticks=$(( ${opts[--wait]} * 100 ))
    if ! zmodload zsh/zselect 2>/dev/null; then
        echo "[ERROR] zsh/zselect module required but not found. Polling cannot continue safely." >&2
        exit ${VDE_ERR_GENERAL:-1}
    fi
    zselect -t ${wait_ticks}
    exit ${VDE_SUCCESS:-0}
fi

# --- 2. SOURCE CORE ECOSYSTEM ---
if [[ -f "${VDE_ROOT_DIR}/lib/vm-common" ]]; then
    source "${VDE_ROOT_DIR}/lib/vm-common"
else
    echo "CRITICAL: lib/vm-common not found."
    exit ${VDE_ERR_GENERAL:-1}
fi
```

### `lib/vm-common`
**Old Text:**
```zsh
    # 2. If cache failed, fall back to JSON/CONF
    if [[ "${use_cache}" -eq 0 ]]; then
        # GLOBAL CONFIGURATION LOCK: Prevent redundant re-smelting
        local global_lock="${VDE_LOCKS_DIR}/global-config.lock"
        claim_lock "${global_lock}" || return ${VDE_ERR_LOCK}
        
        {
```

**New Text:**
```zsh
    # 2. If cache failed, fall back to JSON/CONF
    if [[ "${use_cache}" -eq 0 ]]; then
        # GLOBAL CONFIGURATION LOCK: Prevent redundant re-smelting
        local global_lock="${VDE_LOCKS_DIR}/global-config.lock"
        if [[ "${VDE_NO_LOCK:-0}" != "1" ]]; then
            claim_lock "${global_lock}" || return ${VDE_ERR_LOCK}
        fi
        
        {
```

**Old Text (Closure):**
```zsh
                mv "${cache_tmp}" "${VM_TYPES_CACHE}"
                _info "VM types cached for faster loading"
            fi
        } always {
            release_lock "${global_lock}"
        }
```

**New Text (Closure):**
```zsh
                mv "${cache_tmp}" "${VM_TYPES_CACHE}"
                _info "VM types cached for faster loading"
            fi
        } always {
            if [[ "${VDE_NO_LOCK:-0}" != "1" ]]; then
                release_lock "${global_lock}"
            fi
        }
```

## 3. Spine Rules Hit
- Mandate 24 (Architectural Tagging): Preserved on line 2 for both files (`# @armor (Engine Core)`).
- Universal Agent Rules (ZSH ONLY): All modifications strictly adhere to ZSH syntax without external bash invocations.
- Section 4.5 (Fixed Wait Strike): The wait strike is decoupled from the core ecosystem loading to break the recursive chain.

## 4. Behavioral Changes
The infinite recursion loop between `vde-poll` and `claim_lock` is broken by:
1. Short-circuiting `vde-poll --wait` logic so it processes its wait and exits *before* it tries to load the heavy ecosystem (`lib/vm-common`), ensuring it doesn't trigger another lock request.
2. Introducing `VDE_NO_LOCK` as an explicit safety override to bypass `claim_lock` in `vm-common` when strictly necessary, adding defense-in-depth against lock contention loops.

*Note: Since I mistakenly entered Plan Mode, I am locked to read-only tools and cannot apply these edits directly. Please exit plan mode or apply this remediation manually.*