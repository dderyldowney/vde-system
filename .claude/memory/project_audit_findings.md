---
name: O-1 through O-8 audit findings
description: Full audit of all 8 Docker feature stack step implementations — bugs, fakes, DRY violations, context conflicts, and prioritized fix list
type: project
---

All 8 Docker feature stack phases audited on 2026-03-28. **ALL HIGH/MEDIUM items fixed and committed.**

**Why:** Comprehensive pre-commit audit was run using parallel guardian/reviewer agents after O-8 implementation. Multiple bugs, fake tests, and systemic issues found and resolved.

**How to apply:** Remaining LOW items (FAKE-3, FAKE-4, DRY-2, DRY-3, DRY-6, DRY-7, VDE_ROOT imports, timeouts, cleanup gaps) are systemic improvements — not blockers. Fast baseline: 268 passed / 0 failed confirmed post-fix.

## FIX STATUS SUMMARY

| Item | Status | Commit |
|------|--------|--------|
| BUG-1 through BUG-7 | ✅ FIXED | 23914c3 |
| FAKE-1, FAKE-2, FAKE-5, FAKE-6 | ✅ FIXED | 23914c3 |
| DRY-1, DRY-4, DRY-5 | ✅ FIXED | 4dfbaf9 |
| Context alias (command_exit_code) | ✅ FIXED | 4dfbaf9 |
| Cleanup gap (productivity before-hook) | ✅ FIXED | 4dfbaf9 |
| FAKE-3, FAKE-4 | ⏳ LOW — systemic | — |
| DRY-2, DRY-3, DRY-6, DRY-7 | ⏳ LOW — systemic | — |
| VDE_ROOT import consistency | ⏳ LOW — systemic | — |
| Timeout inconsistencies | ⏳ LOW — systemic | — |
| config_management cleanup gap | ⏳ LOW — systemic | — |

---

## BUGS (HIGH — must fix before commit)

### BUG-1: O-1 double-prefix in vde ps filter
- File: `tests/features/steps/critical_steps.py` lines 307, 315, 321
- Issue: passes `vde ps --filter name=vde-python` but vde-ps auto-prepends `vde-`, resulting in `--filter name=vde-vde-python` → always returns empty → container running checks always return false
- Fix: strip `vde-` prefix before passing to `--filter name=`. Pass `python` not `vde-python`.

### BUG-2: O-8 backup fake path (fake test)
- File: `tests/features/steps/productivity_steps.py` lines 136-139
- Issue: when `data/postgres/` doesn't exist, creates a `.backup_marker` placeholder and silently passes. Test passes in cold CI with no postgres data — fake test.
- Fix: replace else-branch with `assert src.exists(), f"data/postgres/ not found — postgres never started"`. Fail early.

### BUG-3: O-7 rebuild scenario is a no-op (fake test)
- File: `tests/features/steps/configuration_management_steps.py` lines 401-404
- Issue: `step_rebuild_vms` asserts `vde-rebuild` script EXISTS but never executes it. The entire "rebuild" scenario always passes regardless of rebuild logic.
- Fix: execute `run_vde_command("start python --rebuild")` and assert `rc == 0` AND check output contains "Building".

### BUG-4: O-6 direct docker call (VDE CLI violation)
- File: `tests/features/steps/documented_workflow_steps.py` line 578-589
- Issue: `subprocess.run(["docker", "inspect", ...])` — direct docker call, violates VDE CLI mandate.
- Fix: replace with `run_vde_command("inspect python -f '{{.HostConfig.Memory}}'")` and assert Memory value > 0.

### BUG-5: O-2 context variable mismatch
- File: `tests/features/steps/vm_rebuild_steps.py` line 156
- Issue: stores stdout as `context.last_stdout` but `port_management_steps.py:224` reads `context.last_output` for the "Unknown VM" assertion. Cross-file scenario reads stale value.
- Fix: change line 156 to `context.last_output = result.stdout` (or set both).

### BUG-6: NameError in shell_helpers.py
- File: `tests/features/steps/shell_helpers.py` line 312
- Issue: calls `_get_container_name(vm_name)` but `_get_container_name` is never bound — import aliases it as `_get_container_name_canonical`. Will raise `NameError` at runtime if `normalize_vm_name()` is ever called.
- Fix: fix the reference to match the actual import alias.

### BUG-7: Container cleanup never fires for integration scenarios
- File: `tests/features/environment.py` line 462
- Issue: container cleanup in `after_scenario` hook is gated on `context._docker_cleanup_needed = True`. This flag is NEVER set in `docker_management_steps.py` or `productivity_steps.py`. Containers leak on scenario failure.
- Fix: add `context._docker_cleanup_needed = True` in any `@given` step that starts a container in these two files.

---

## FAKE / PINK TESTS (MEDIUM)

### FAKE-1: O-2/O-3 rebuild assertions are exit-code only
- File: `tests/features/steps/vm_rebuild_steps.py` lines 88-107
- Steps: `docker-compose up --build should be executed`, `--no-cache should be executed`, `image should be rebuilt`
- All three assert only `context.last_exit_code == 0`. No verification docker-compose ran with `--build`.
- Fix: check `context.last_error` or `context.last_output` for "Building" keyword from docker-compose.

### FAKE-2: O-4 compose operation assertions are exit-code only
- File: `tests/features/steps/docker_operations_steps.py` lines 239-275
- Steps: `compose build/up/down should be executed` — all three assert only `last_exit_code == 0`.
- Fix: same as FAKE-1 — inspect output for operation-specific keywords.

### FAKE-3: O-7 env vars auto-loaded checks directory not runtime
- File: `tests/features/steps/configuration_management_steps.py` lines 464-471
- Asserts `env-files/` directory exists, not that VDE loads the file when starting a VM.
- Fix: run `vde exec <vm> printenv NODE_ENV` after `vde start` to verify runtime loading.

### FAKE-4: O-7 unhealthy VMs restart checks script existence not behavior
- File: `tests/features/steps/configuration_management_steps.py` lines 803-805
- Asserts `vde-health` script exists. Does not verify unhealthy containers are restarted.
- Fix: query `vde ps` for health status; trigger a health failure; confirm restart occurs.

### FAKE-5: O-8 fresh_db_test dead assignment
- File: `tests/features/steps/productivity_steps.py` lines 72-75
- `context.fresh_db_test = True` set but never read by any subsequent step.
- Fix: use it in `step_should_have_fresh_database` as a guard, or remove the assignment.

### FAKE-6: O-8 backup scenario never restores
- File: `tests/features/steps/productivity_steps.py` lines 144-153
- "Database backups and restores" scenario verifies backup directory exists but never restores to postgres. Scenario name is misleading.
- Fix: add restore step: stop postgres → remove data volume → copy backup back → restart postgres → query for sentinel row `persistence-check`.

---

## CROSS-CUTTING DRY VIOLATIONS

### DRY-1: Three parallel container-state checker implementations
- `vm_rebuild_steps.py:20-31`, `docker_operations_steps.py:27-31`, `vm_common.py:104-144`
- All implement "is container running?" independently. Canonical is `vm_common.container_is_running()`.
- Fix: delete private copies in vm_rebuild_steps and docker_operations_steps; import from vm_common.

### DRY-2: Duplicate _load_vm_types()
- `critical_steps.py:75` vs `configuration_management_steps.py:22`
- Same source file, different return types (tuple vs raw dict).
- Fix: single loader in vm_common.py returning raw dict; callers extract what they need.

### DRY-3: Duplicate compose-file path computation
- `docker_operations_steps.py:40-43`, `vm_common.py:172-183`, `critical_steps.py` (inline)
- `vm_common.get_compose_file()` already exported — all should use it.

### DRY-4: Log-line filter regex duplicated 3x
- `critical_steps.py` lines 188, 206, 624 — identical `r"^\d{4}-\d{2}-\d{2}|^\[INFO\]"` pattern.
- Fix: extract to module-level constant `_LOG_LINE_RE`.

### DRY-5: SERVICE_VMS and ALL_SERVICE_VMS identical frozensets
- `shell_helpers.py:271-293` — two frozensets with identical content; one unused as distinct.
- Fix: define one constant; delete duplicate.

### DRY-6: Near-identical SSH port step text (collision risk)
- `critical_steps.py:267`: `'no two VMs should share the same SSH port'`
- `docker_management_steps.py:224`: `'no two VMs should have the same SSH port'`
- Semantically identical, different implementations (static vs runtime). If a feature file uses wrong phrasing, Behave silently binds to the first-loaded.
- Fix: consolidate to one step text and one implementation.

### DRY-7: O-6 workspace host-path resolution duplicated
- `docker_management_steps.py:379-392` vs `401-425` — identical 8-line block.
- Fix: extract to `_resolve_workspace_host_path(vm_name)` helper.

---

## CONTEXT VARIABLE CONFLICTS (systemic)

| Variable | Conflict |
|---|---|
| `context.vm_name` | Raw name (`"python"`) in most files; `vm_common.ensure_vm_running()` sets it prefixed (`"vde-python"`) |
| `context.last_exit_code` vs `context.command_exit_code` | `run_vde_command()` sets `last_exit_code`; `critical_steps.py` sets `command_exit_code` |
| `context.last_output` vs `context.command_output` vs `context.last_stdout` | Three names for stdout |
| `context.vde_command_output` | Combined stdout+stderr from `run_vde_command()` — inconsistently used |

**Fix:** Add canonical variable contract as a comment block in vm_common.py:
- `context.vm_name` = raw name without `vde-` prefix (never the container name)
- `context.last_exit_code` = last command exit code
- `context.last_output` = last command stdout
- `context.last_error` = last command stderr
Alias `context.command_exit_code` → `context.last_exit_code` in critical_steps.py.

---

## VDE_ROOT IMPORT INCONSISTENCY

Four files import `VDE_ROOT` directly from `config` (bypassing VDE_PROJECT_ROOT override):
- `critical_steps.py`, `vm_rebuild_steps.py`, `docker_operations_steps.py`, `common_steps.py`

Three files import via `vm_common` (VDE_PROJECT_ROOT respected):
- `configuration_management_steps.py`, `productivity_steps.py`, `docker_management_steps.py`

Fix: all files import from vm_common to uniformly respect VDE_PROJECT_ROOT.

---

## TIMEOUT INCONSISTENCIES

| Operation | Too-short location | Recommended |
|---|---|---|
| `vde start` | `docker_management_steps.py:184` (120s multi-VM loop) | 300s |
| `vde stop` | `docker_management_steps.py:33` `_cleanup_vm` (30s) | 60s minimum |
| `vde start --rebuild --no-cache` | `vm_rebuild_steps.py:83` (1200s) | Cap at 600s |
| `vde start postgres` | `docker_management_steps.py:259` (120s) | 300s |

---

## CLEANUP GAPS

1. `configuration_management_steps.py`: `_cleanup_test_vm_type()` called inside `@then` bodies — if THEN step fails before cleanup call, `test-cfg-*` entries persist in `vm-types.json` permanently.
   Fix: move cleanup to `@after_scenario` hook or use `context.add_cleanup()`.

2. `productivity_steps.py`: No Before hook to guarantee postgres is absent at scenario start. Scenario 2 (fresh database) may pass spuriously if prior scenario left postgres running.
   Fix: add scenario-level Before hook that stops+removes postgres.

---

## PRIORITIZED FIX ORDER FOR NEXT SESSION

1. BUG-1 — O-1 double-prefix (container checks always false)
2. BUG-6 — shell_helpers.py NameError (latent crash)
3. BUG-7 — _docker_cleanup_needed never set (container leaks)
4. BUG-2 — O-8 backup fake path
5. BUG-3 — O-7 rebuild no-op
6. BUG-4 — O-6 direct docker call
7. BUG-5 — O-2 context variable mismatch
8. FAKE-1/FAKE-2 — rebuild/compose assertions (exit-code only)
9. FAKE-6 — O-8 backup scenario missing restore
10. DRY-1 — consolidate container-state checkers
11. Context variable contract (vm_common.py canonical names)
12. VDE_ROOT import consistency
13. Remaining DRY, timeout, cleanup gaps
