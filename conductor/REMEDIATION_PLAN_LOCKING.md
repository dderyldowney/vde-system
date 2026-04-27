# Stale Lock Buster & VDE Poll Process Explosion Remediation Plan
<!-- @shared-law (Forge Component) -->

## Objective
Fix the infinite recursion/process explosion in `vde-poll` due to float math errors with `zselect`, and implement a Stale Lock Buster in `lib/vm-lock` to handle dead PIDs holding locks or queue tickets.

## Background & Motivation
Currently, `lib/vm-lock` attempts to acquire a lock atomically. If it fails, it waits by calling `bin/vde-poll --wait <jitter_sec>`.
1. The `<jitter_sec>` is calculated using floating-point math (e.g., `0.362`).
2. `vde-poll` multiplies this by 100 to get deciseconds for `zselect -t`. Zsh math evaluates this to a float (e.g., `36.2`).
3. `zselect -t` strictly requires an integer. It throws an error and exits immediately because of `set -e`.
4. `claim_lock` sees `vde-poll` exit and instantly loops without waiting, repeatedly spawning `vde-poll` and causing a massive process explosion that drives up system load.
5. In addition, if a process holding the lock dies (e.g., killed or crashed), the lock and queue tickets remain indefinitely, causing all other operations to hang.

## Proposed Solution

1. **Fix `bin/vde-poll` Float Error:**
   - Modify the `--wait` logic in `bin/vde-poll` to safely truncate any floating-point results to an integer before passing it to `zselect -t`.
   - Ensure the interval loop math (for standard polling) also truncates decimals if `INTERVAL` is a float.

2. **Implement Stale Lock Buster in `lib/vm-lock`:**
   - Inside the contention `while` loop, when checking `pid_file` ownership, extract the owner's PID.
   - Check process liveness using `kill -0 "${owner_pid}" 2>/dev/null`.
   - If the PID is dead, log a warning, forcefully remove the lock directory (`rm -rf "${lock_file}"`), and `continue` to attempt the lock acquisition immediately.
   - Do the same for stale queue tickets (`rm -f "${queue_dir}/${oldest_ticket}"`) by extracting the PID from the ticket filename (`${oldest_ticket##*-}`).

## Implementation Steps

1. Modify `bin/vde-poll`:
   ```zsh
   # Truncate floating-point values to integers using parameter expansion
   local wait_ticks=$(( ${opts[--wait]} * 100 ))
   wait_ticks=${wait_ticks%.*} # Strip decimal portion
   ```
   Do the same for the `INTERVAL` polling calculation:
   ```zsh
   local wait_ticks=$(( INTERVAL * 100 ))
   wait_ticks=${wait_ticks%.*}
   ```

2. Modify `lib/vm-lock`:
   ```zsh
        # LOCK CONTENTION TRANSPARENCY & STALE LOCK BUSTER
        local owner_info=""
        if [[ -f "${pid_file}" ]]; then
            local pid_data=$(cat "${pid_file}" 2>/dev/null)
            local owner_pid="${pid_data%%:*}"
            owner_info="PID ${owner_pid}"
            
            # THE STALE LOCK BUSTER (Phase 32)
            if [[ -n "${owner_pid}" ]] && ! kill -0 "${owner_pid}" 2>/dev/null; then
                vde_log_warn "Busting stale lock ${lock_file} (Owner PID ${owner_pid} is dead)" "lock"
                rm -rf "${lock_file}" 2>/dev/null
                continue
            fi
        elif [[ "${oldest_ticket}" != "${ticket_id}" ]]; then
            owner_info="Queue position: waiting for ${oldest_ticket#*-}"
            
            # THE STALE TICKET BUSTER (Phase 32)
            local ticket_pid="${oldest_ticket##*-}"
            if [[ -n "${ticket_pid}" ]] && ! kill -0 "${ticket_pid}" 2>/dev/null; then
                vde_log_warn "Busting stale ticket ${oldest_ticket} (Owner PID ${ticket_pid} is dead)" "lock"
                rm -f "${queue_dir}/${oldest_ticket}" 2>/dev/null
                continue
            fi
        fi
   ```

## Verification & Test Hardening
1. **Test Wrapper (Resource Protection)**:
   - Modify `tests/features/steps/locking_steps.py` to use `os.setsid` when spawning the `vde-poll` contender so we can reliably kill the entire process tree (Process Group) if it runs out of bounds.
   - When executing the behave test in the terminal, wrap the execution with a strict Python-based timeout (e.g., `python3 -c "import subprocess; subprocess.run(['python3', '-m', 'behave', ...], timeout=15)"`) to guarantee the session does not hang and require a manual `Ctrl+C`.

2. Execute the tests:
   - Ensure all 3 Scenarios pass:
     - `Stale Lock Buster (Crashed Process)`
     - `Stale Ticket Buster (Queued Process)`
     - `Process Explosion Protection (Recursion Break)`