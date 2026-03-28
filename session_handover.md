# Session Handover — Docker Feature Stack

**Mission:** Validate core Docker infrastructure, then stack Docker-tagged features one by one.
**Rule:** Step files must use `bin/vde` CLI — no direct `docker` subprocess calls.

> **STARTUP ACTION REQUIRED:** Read `/Users/dderyldowney/.claude/projects/-Users-dderyldowney-VDE/memory/project_audit_findings.md`
> before doing anything else. It contains the prioritized fix list (7 bugs, 6 fake tests) that
> must be resolved before the O-8 code can be committed. This is not optional context — it is
> the active work queue for this session.

---

## CURRENT STATE (2026-03-28 end of session)

### ALL 8 PHASES COMPLETE — BUT NOT YET COMMITTED

Code is written and fast baseline passes (268/0), but a full pre-commit audit found
**7 bugs, 6 fake/pink tests, and systemic DRY/context issues** that must be fixed before commit.

See full audit: `/Users/dderyldowney/.claude/projects/-Users-dderyldowney-VDE/memory/project_audit_findings.md`

### Phase Status

| # | Feature | Scenarios | Result |
|---|---------|-----------|--------|
| 1 | `critical-path.feature` | 14 | ✅ 14/14 |
| 2 | `vm-lifecycle.feature` | 15 | ✅ RESOLVED |
| 3 | `vm-rebuild.feature` | 8 | ✅ 8/8 |
| 4 | `docker-operations.feature` | 12 | ✅ 12/12 |
| 5 | `vm-full-lifecycle.feature` | 1 | ✅ 1/1 (25/25 steps) |
| 6 | `docker-management.feature` | 13 | ✅ 13/13 |
| 7 | `configuration-management.feature` | 23 | ✅ 23/23 |
| 8 | `productivity.feature` | 4 | ✅ 4/4 (O-8) |

**Fast baseline:** 268 passed / 0 failed / 187 skipped (confirmed 2026-03-28)

---

## NEXT SESSION — START HERE

### Step 1: Load audit findings
Read `/Users/dderyldowney/.claude/projects/-Users-dderyldowney-VDE/memory/project_audit_findings.md`
This has the full prioritized fix list with file:line references.

### Step 2: Fix in priority order (HIGH bugs first)

**CRITICAL — fix first:**

1. **BUG-1** `critical_steps.py:307,315,321` — vde ps `--filter name=vde-python` double-prefixes to `vde-vde-python`. Strip `vde-` before passing. Container running checks always return false currently.

2. **BUG-6** `shell_helpers.py:312` — `_get_container_name` unbound (import alias mismatch). Will raise `NameError` at runtime.

3. **BUG-7** `environment.py:462` — `_docker_cleanup_needed` flag never set in `docker_management_steps.py` or `productivity_steps.py`. Add `context._docker_cleanup_needed = True` in any `@given` that starts a container in those files.

4. **BUG-2** `productivity_steps.py:136-139` — backup else-branch creates placeholder `.backup_marker` when `data/postgres/` absent → fake test passes in cold CI. Replace with `assert src.exists()`.

5. **BUG-3** `configuration_management_steps.py:401-404` — `step_rebuild_vms` never executes vde-rebuild. Always passes. Fix: run `run_vde_command("start python --rebuild")` + assert output contains "Building".

6. **BUG-4** `documented_workflow_steps.py:578` — `subprocess.run(["docker", "inspect", ...])` direct docker call. Replace with `run_vde_command("inspect python ...")` + assert Memory > 0.

7. **BUG-5** `vm_rebuild_steps.py:156` — stores `context.last_stdout` but `port_management_steps.py:224` reads `context.last_output`. Fix: set both or rename.

**FAKE TESTS — fix after bugs:**

8. **FAKE-1** `vm_rebuild_steps.py:88-107` — rebuild steps assert only exit code. Add output check for "Building" keyword.

9. **FAKE-2** `docker_operations_steps.py:239-275` — compose build/up/down assert only exit code. Add output check.

10. **FAKE-6** `productivity_steps.py:144-153` — backup scenario never restores. Add: stop postgres → copy backup back → restart → query sentinel row `persistence-check`.

**DRY + systemic — fix after fakes:**

11. **DRY-1** Consolidate three `_is_container_running()` implementations → use `vm_common.container_is_running()` everywhere.

12. **Context contract** — document canonical names in `vm_common.py`; alias `command_exit_code` → `last_exit_code` in `critical_steps.py`.

13. All remaining DRY, timeout, VDE_ROOT import, cleanup gaps — see full audit file.

### Step 3: Re-run fast baseline
```
python3 -m behave --tags="not @integration" --no-capture 2>&1 | tail -5
# Must show: 268 passed / 0 failed
```

### Step 4: Re-run dry-run on each feature
```
python3 -m behave --dry-run tests/features/core-infrastructure/productivity.feature
# Repeat for each feature if step text was changed
```

### Step 5: /vde-review → /vde-commit

---

## WHAT WAS DONE THIS SESSION (2026-03-28)

### O-8 — productivity.feature (implemented, NOT committed)
- Created `tests/features/steps/productivity_steps.py` — 10 step defs
- Covers all 4 scenarios: data persistence, clean-state teardown, backup creation, background services
- Step reword: `When I stop and restart postgres VM` → `When I stop and restart PostgreSQL` (matched existing def)
- `_seed_postgres_table()` helper for DRY seeding logic
- Fast baseline confirmed: 268 passed / 0 failed
- Dry-run: all 13 steps resolved (0 undefined)
- Guardian: CLEAN | Reviewer: APPROVED | Enforcer: PASS
- **Audit then found BUG-2 (backup fake path) and FAKE-6 (no restore) — must fix**

### Full audit run (O-1 through O-8)
- Spawned 3 parallel guardian agents (O-1–O-4, O-5–O-8, cross-cutting)
- Found 7 bugs, 6 fake/pink tests, 7 DRY violations, context variable conflicts, timeout inconsistencies
- All findings saved to memory/project_audit_findings.md

---

## FAST TEST BASELINE

```
Fast tests (--tags="not @integration"): 268 passed / 0 failed / 187 skipped
Runtime: ~2.5 minutes
```

Do not regress this baseline.

---

## DOCKER FEATURE STACK ORDER

| # | Feature | Status |
|---|---------|--------|
| 1 | `critical-path.feature` | ✅ DONE (needs BUG-1 fix) |
| 2 | `vm-lifecycle.feature` | ✅ DONE (needs BUG-5 fix) |
| 3 | `vm-rebuild.feature` | ✅ DONE (needs FAKE-1 fix) |
| 4 | `docker-operations.feature` | ✅ DONE (needs FAKE-2 fix) |
| 5 | `vm-full-lifecycle.feature` | ✅ DONE |
| 6 | `docker-management.feature` | ✅ DONE (needs BUG-4, BUG-7 fix) |
| 7 | `configuration-management.feature` | ✅ DONE (needs BUG-3, FAKE-3, FAKE-4 fix) |
| 8 | `productivity.feature` | ✅ DONE (needs BUG-2, FAKE-6, BUG-7 fix) |

---

## STEP DEF STRATEGY

- All new step defs go in appropriate existing file (no new files unless no fit)
- Docker state checks → `vde ps -q` (running) or `vde ps --all -q` (any state)
- Stop → `vde stop {vm_name}`
- Remove → `vde remove {vm_name}`
- Network checks → `vde networks`
- **Never use direct `docker` subprocess calls in step files**
- **All files should import VDE_ROOT via vm_common (not directly from config)**

---

## KEY FILE MAP

| File | Phase | Lines | Notes |
|------|-------|-------|-------|
| `tests/features/steps/critical_steps.py` | O-1 | ~681 | Has BUG-1 (double-prefix), uses own `_vde_cli()` not `run_vde_command` |
| `tests/features/steps/vm_rebuild_steps.py` | O-2/O-3 | ~271 | Has BUG-5 (last_stdout), FAKE-1 (rebuild assertions) |
| `tests/features/steps/docker_operations_steps.py` | O-4 | ~447 | Has FAKE-2 (compose assertions), DRY-1 (container checker) |
| `tests/features/steps/docker_management_steps.py` | O-6 | ~973 | Has BUG-7 (cleanup flag), DRY-7 (workspace path) |
| `tests/features/steps/configuration_management_steps.py` | O-7 | ~1128 | Has BUG-3 (rebuild no-op), FAKE-3, FAKE-4 |
| `tests/features/steps/productivity_steps.py` | O-8 | ~180 | Has BUG-2 (fake backup), FAKE-6 (no restore) |
| `tests/features/steps/documented_workflow_steps.py` | O-6 shared | ~698 | Has BUG-4 (direct docker call line 578) |
| `tests/features/steps/shell_helpers.py` | shared | ~313 | Has BUG-6 (NameError line 312) |
| `tests/features/steps/vm_common.py` | shared | ~639 | Canonical helpers — all other files should import from here |
| `tests/features/environment.py` | shared | — | Has BUG-7 root (_docker_cleanup_needed gate line 462) |

---

## FUTURE: Config Directory Reordering

**Proposed:** Move from `configs/docker/{python,postgres,...}` to:
- `configs/docker/languages/{python,rust,...}`
- `configs/docker/services/{postgres,redis,...}`

**Required changes (when implemented):**
- All bin/* scripts using CONFIGS_DIR path construction
- All test step definitions checking config paths
- docker-compose template generation (vde-templates)
- Update CONFIGS_DIR default and path construction logic
