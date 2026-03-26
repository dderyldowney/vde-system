# Session Handover — Docker Feature Stack

**Mission:** Validate core Docker infrastructure, then stack Docker-tagged features one by one.
**Rule:** Step files must use `bin/vde` CLI — no direct `docker` subprocess calls.

---

## CURRENT STATE (2026-03-26 end of session)

### Phase 0 Results

| # | Feature | Scenarios | Result |
|---|---------|-----------|--------|
| 1 | `critical-path.feature` | 14 | ✅ 14/14 |
| 2 | `vm-lifecycle.feature` | 15 | ⚠️ 14/15 |
| 3 | `vm-rebuild.feature` | 8 | ✅ 8/8 |

**Fast baseline:** 268 passed / 0 failed (unchanged)

---

## OUTSTANDING FAILURE — MUST FIX FIRST

**Feature:** `vm-lifecycle.feature`
**Failure:** `ASSERT FAILED: VM python is still running`
**Most likely scenario:** "Stop a running VM" or "Stop all running VMs"

**Root cause:** `_container_running()` in `vm_rebuild_steps.py` was refactored from `docker ps` to `vde ps -q`. After `vde stop python`, the container may still briefly appear in `vde ps -q` (timing), or `vde stop` (graceful shutdown) takes longer than the direct `docker stop` it replaced.

**Next session: diagnose first.**
```zsh
# Run the failing scenario in isolation to get full output:
python3 -m behave tests/features/core-infrastructure/vm-lifecycle.feature:42 -q
python3 -m behave tests/features/core-infrastructure/vm-lifecycle.feature:48 -q
```

**Fix options:**
1. Add a wait/poll loop in `_container_running()` after stop commands
2. Check if `vde ps -q` output has timing lag vs docker ps
3. Or use `vde status` which reads .docker-state/ files (may be more reliable)

---

## WHAT WAS DONE THIS SESSION

### Fixes in vm_rebuild_steps.py
1. Hardcoded step `'I run "vde restart python"'` → `'I run "vde restart {vm_name}"'`
2. Hardcoded step `'I run "vde start python --rebuild"'` → `'I run "vde start {vm_name} --rebuild"'`
3. Added missing `Given VM types are loaded from configuration` step
4. `context.vm_name = vm_name` in `step_vde_restart` (needed by `step_fresh_container`)
5. Fixed `step_fresh_container` — VDE restart creates new container so RestartCount=0 is correct
6. `step_config_still_exists` — now actually asserts compose_file.exists()
7. **Full rewrite to remove all direct docker calls** — uses `vde ps -q`, `vde stop`, `vde remove`

### Fixes in critical_steps.py
- `container "vde-python" is running` → `_vde_cli("ps -q")`
- Network existence/bridge type checks → `_vde_cli("networks")`

### Fix in lib/vde-errors
- `vde_error_vm_not_found` → "Unknown VM: '{name}'" (was "VM '{name}' not found")
- Matches VDE-SPEC.md §10: `VDE_ERR_NOT_FOUND` → "Unknown VM: $VM_NAME"

---

## FAST TEST BASELINE

```
Fast tests (--tags="not @integration"): 268 passed / 0 failed / 0 errors / 187 skipped
Runtime: ~2 minutes
```

Do not regress this baseline.

---

## DOCKER FEATURE STACK ORDER (next features)

After fixing the vm-lifecycle stop failure, proceed to:

| # | Feature | Status |
|---|---------|--------|
| 4 | `docker-operations.feature` | 12 scenarios, 121 undefined steps — write step defs |
| 5 | `vm-full-lifecycle.feature` | 1 scenario, 16 undefined steps — write step defs |
| 6 | `docker-management.feature` | 11 scenarios — write step defs |
| 7 | `configuration-management.feature` | 5 scenarios |
| 8 | `productivity.feature` | 4 scenarios |

---

## STEP DEF STRATEGY

- All new step defs go in appropriate existing file (no new files unless no fit)
- Docker state checks → `vde ps -q` (running) or `vde ps --all -q` (any state)
- Stop → `vde stop {vm_name}`
- Remove → `vde remove {vm_name}`
- Network checks → `vde networks`
- **Never use direct `docker` subprocess calls in step files**
